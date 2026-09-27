"""Optional diagram practice, separate from the topic's conversation and reflection."""
from fastapi import File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field, field_validator
from app.services import vision


class CaptionInput(BaseModel):
    text: str = Field(min_length=1, max_length=4000)

    @field_validator('text', mode='before')
    @classmethod
    def strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value


def add_diagram_routes(router, store, session_lock, detail):
    @router.post('/{sid}/diagram-practices', status_code=201)
    def create(sid: str, file: UploadFile = File(...), page: int = Form(...),
               request_id: str = Form(..., min_length=1, max_length=100)):
        with session_lock(sid):
            if store.diagram(sid):
                raise HTTPException(409, 'Open the original notes session to create another diagram practice.')
            document = store.document(sid)
            if not document:
                raise HTTPException(409, 'Upload notes before adding a diagram.')
            if page < 1 or page > document['page_count']:
                raise HTTPException(422, 'Choose a page within your uploaded notes.')
            try:
                image, metadata = vision.prepare_image(file.file.read(vision.MAX_IMAGE_BYTES + 1))
            except ValueError as exc:
                raise HTTPException(422, str(exc)) from exc
            prior = store.diagram_request(sid, request_id)
            if prior:
                previous = store.diagram(prior)
                if previous['page'] != page or previous['trace']['original_sha256'] != metadata['original_sha256']:
                    raise HTTPException(409, 'This request identifier was used for a different diagram.')
                return detail(prior)
            try:
                caption, trace = vision.describe(image)
            except Exception as exc:
                raise HTTPException(503, 'Granite could not describe this image. Check that granite3.2-vision:2b is installed in Ollama, then retry. No new practice was saved.') from exc
            title = f"{store.get(sid)['name'][:65]} · Diagram on page {page}"
            child = store.create_diagram(sid, request_id, title, page, image, caption, {**trace, **metadata})
            return detail(child)

    @router.get('/{sid}/diagram.png')
    def image(sid: str):
        diagram = store.diagram(sid, include_image=True)
        if not diagram:
            raise HTTPException(404, 'No diagram belongs to this practice.')
        return Response(diagram['image'], media_type='image/png')

    @router.post('/{sid}/diagram/approve')
    def approve(sid: str, body: CaptionInput):
        with session_lock(sid):
            if not store.diagram(sid):
                raise HTTPException(404, 'No diagram belongs to this practice.')
            if store.run(sid):
                raise HTTPException(409, 'The description is fixed once practice starts, so saved evidence stays consistent.')
            store.approve_diagram(sid, body.text)
            return detail(sid)
