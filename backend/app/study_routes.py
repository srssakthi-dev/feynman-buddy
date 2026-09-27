"""Session-scoped notes, grounded dialogue and final reflection."""
import threading
from contextlib import contextmanager
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field, field_validator
from app.services.documents import extract_notes, MAX_BYTES
from app.services import inference
from app.services.evidence import reply_sources
from app.services import speech
from app.services import vision
from app.diagram_routes import add_diagram_routes


class TurnInput(BaseModel):
    text: str = Field(min_length=1, max_length=1200)
    request_id: str = Field(min_length=1, max_length=100)
    transcription_id: str | None = Field(default=None, max_length=100)

    @field_validator("text", mode="before")
    @classmethod
    def strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value


def create_study_router(store):
    router = APIRouter(prefix="/api/sessions")
    locks = {}
    locks_guard = threading.Lock()

    def require_session(sid):
        session = store.get(sid)
        if not session:
            raise HTTPException(404, "Study session not found.")
        return session

    @contextmanager
    def session_lock(sid):
        require_session(sid)
        with locks_guard:
            lock = locks.setdefault(sid, threading.Lock())
        if not lock.acquire(blocking=False):
            raise HTTPException(409, "This session is still processing. Please wait.")
        try:
            yield
        finally:
            lock.release()

    def detail(sid):
        session = require_session(sid)
        document = store.document(sid)
        if document:
            document.pop("vectors", None)
        run = store.run(sid)
        messages = store.messages(sid)
        return {"session": session, "document": document, "messages": messages,
                "diagram": store.diagram(sid),
                "reply_sources": reply_sources(messages, store.traces(sid)),
                "started": run is not None, "finished": bool(run and run["finished"]),
                "reflection": run["reflection"] if run else None,
                "model": run["model"] if run else inference.MODEL,
                "prompt_version": run["prompt_version"] if run else inference.PROMPT_VERSION}

    @router.get("/{sid}/study")
    def read_study(sid: str):
        return detail(sid)

    @router.post("/{sid}/documents", status_code=201)
    def upload(sid: str, file: UploadFile = File(...)):
        with session_lock(sid):
            if store.document(sid):
                raise HTTPException(409, "This session already has notes. Create another session to use a different PDF.")
            data = file.file.read(MAX_BYTES + 1)
            try:
                notes = extract_notes(data, file.filename or "notes.pdf")
            except ValueError as exc:
                raise HTTPException(422, str(exc)) from exc
            try:
                vectors = inference.embed(notes["chunks"])
            except Exception as exc:
                raise HTTPException(503, "The local embedding model could not load. Your file was not saved; retry once it is available.") from exc
            store.save_document(sid, notes, data, vectors)
            return detail(sid)

    @router.get("/{sid}/notes.pdf")
    def pdf(sid: str):
        require_session(sid)
        document = store.document(sid, include_pdf=True)
        if not document:
            raise HTTPException(404, "No notes have been uploaded to this session.")
        return Response(document["pdf"], media_type="application/pdf",
                        headers={"Content-Disposition": 'inline; filename="study-notes.pdf"'})

    @router.post("/{sid}/start")
    def start(sid: str):
        with session_lock(sid):
            if store.run(sid):
                return detail(sid)
            if not store.document(sid):
                raise HTTPException(409, "Upload your notes before starting.")
            name = store.get(sid)["name"]
            diagram = store.diagram(sid)
            if diagram and not diagram['approved_caption']:
                raise HTTPException(409, 'Review and save the diagram description before starting.')
            opening = ("Hey! Can you walk me through what this diagram is showing? Start with whatever you notice."
                       if diagram else f"Hey! What are you going to teach me about {name} today? Start wherever feels natural.")
            store.start(sid, inference.MODEL,
                        'diagram-conversation-v1' if diagram else inference.PROMPT_VERSION, opening)
            return detail(sid)

    @router.post("/{sid}/turn")
    def turn(sid: str, body: TurnInput):
        with session_lock(sid):
            run = store.run(sid)
            if not run:
                raise HTTPException(409, "Start your teaching session first.")
            prior = store.prior_request(sid, body.request_id)
            if prior:
                if prior["student_text"] != body.text:
                    raise HTTPException(409, "This request identifier was used for a different message.")
                return detail(sid)
            if run["finished"]:
                raise HTTPException(409, "This practice is finished. Create a new session to practise again.")
            messages = store.messages(sid)
            if sum(m["role"] == "student" for m in messages) >= 8:
                raise HTTPException(409, "This short practice has reached eight responses. Finish and reflect, then start a fresh session.")
            topic = store.get(sid)["name"]
            transcription = None
            if body.transcription_id:
                transcription = store.transcription(sid, body.transcription_id)
                if transcription is None:
                    raise HTTPException(422, 'This transcript does not belong to this session.')
            try:
                diagram = store.diagram(sid)
                query = topic + "\n" + messages[-1]["text"] + "\n" + body.text
                if diagram:
                    query += '\nDiagram context: ' + diagram['approved_caption'][:1500]
                sources = inference.retrieve(store.document(sid), query)
                if diagram:
                    sources = [vision.diagram_source(diagram), *sources]
                answer, trace = inference.reply(topic, messages, body.text, sources, run["model"])
            except Exception as exc:
                raise HTTPException(503, "Your buddy could not reply. Check that Ollama is running with the local model, then retry. Your message has not been saved twice.") from exc
            trace["sources"] = sources
            if transcription:
                trace['transcription'] = transcription
                trace['transcription']['edited_before_send'] = transcription['text'] != body.text
            store.save_turn(sid, body.request_id, body.text, answer, trace)
            return detail(sid)

    @router.post('/{sid}/transcribe')
    def transcribe_recording(sid: str, file: UploadFile = File(...)):
        with session_lock(sid):
            run = store.run(sid)
            if not run or run['finished']:
                raise HTTPException(409, 'Start an unfinished practice before recording.')
            if sum(m['role'] == 'student' for m in store.messages(sid)) >= 8:
                raise HTTPException(409, 'Finish this practice before starting another recording.')
            data = file.file.read(speech.MAX_AUDIO_BYTES + 1)
            try:
                text, trace = speech.transcribe(data)
            except ValueError as exc:
                raise HTTPException(422, str(exc)) from exc
            except Exception as exc:
                raise HTTPException(503, 'Local transcription is unavailable. Check the Whisper installation or type your explanation.') from exc
            return store.save_transcription(sid, text, trace)

    @router.post("/{sid}/finish")
    def finish(sid: str):
        with session_lock(sid):
            run = store.run(sid)
            if not run:
                raise HTTPException(409, "Start your teaching session first.")
            if run["finished"]:
                return detail(sid)
            messages = store.messages(sid)
            students = [message for message in messages if message["role"] == "student"]
            if not students:
                raise HTTPException(409, "Share an explanation before asking for a reflection.")
            try:
                # Cover the conversation with passages actually retrieved across turns.
                collected = {}
                for trace in store.traces(sid):
                    for source in trace["sources"]:
                        if source.get('kind') == 'reviewed_diagram_description':
                            continue  # Included explicitly below, never assigned a fake retrieval score.
                        existing = collected.get(source["id"])
                        if existing is None or source["similarity"] > existing["similarity"]:
                            collected[source["id"]] = source
                sources = sorted(collected.values(), key=lambda item: item["similarity"], reverse=True)[:6]
                diagram = store.diagram(sid)
                if diagram:
                    sources = [vision.diagram_source(diagram), *sources[:5]]
                reflection, trace = inference.reflect(store.get(sid)["name"], messages, sources, run["model"])
            except Exception as exc:
                raise HTTPException(503, "The reflection could not be generated. Your conversation is saved; please retry.") from exc
            store.finish(sid, reflection, trace)
            return detail(sid)

    @router.get("/{sid}/export")
    def export(sid: str):
        result = detail(sid)
        result["traces"] = store.traces(sid)
        result["scope"] = "Provisional practice reflection, not a grade or validated mastery measure."
        return result

    add_diagram_routes(router, store, session_lock, detail)
    return router
