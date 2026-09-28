"""Figures attached to the existing topic conversation (no child practice)."""
from fastapi import File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field, field_validator
from app.services import blip, vision


class FigureReview(BaseModel):
    text: str = Field(min_length=1, max_length=4000)

    @field_validator('text', mode='before')
    @classmethod
    def strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value


def add_topic_figure_routes(router, store, session_lock, detail):
    @router.post('/{sid}/figures', status_code=201)
    def upload_figure(sid: str, file: UploadFile = File(...), page: int = Form(...),
                      request_id: str = Form(..., min_length=1, max_length=100),
                      printed_caption: str = Form(default='', max_length=500)):
        with session_lock(sid):
            document = store.document(sid)
            if not document:
                raise HTTPException(409, 'Upload your notes before adding a figure.')
            if store.diagram(sid):
                raise HTTPException(409, 'Figures in the topic conversation belong to the original notes session.')
            if page < 1 or page > document['page_count']:
                raise HTTPException(422, 'Choose a page within your uploaded notes.')
            if store.run(sid) and store.run(sid)['finished']:
                raise HTTPException(409, 'This practice is finished. Create a new session to add a figure.')
            try:
                image, metadata = vision.prepare_image(file.file.read(vision.MAX_IMAGE_BYTES + 1))
            except ValueError as exc:
                raise HTTPException(422, str(exc)) from exc
            previous_id = store.figure_request(sid, request_id)
            if previous_id:
                previous = store.figure(sid, previous_id)
                if (previous['page'] != page or previous['trace']['original_sha256'] != metadata['original_sha256']
                        or previous['printed_caption'] != printed_caption.strip()):
                    raise HTTPException(409, 'This request identifier was used for a different figure.')
                return detail(sid)
            if len(store.figures(sid)) >= 3:
                raise HTTPException(409, 'This short session supports up to three selected figures.')
            try:
                caption, trace = blip.describe(image)
            except Exception as exc:
                raise HTTPException(503, 'Local BLIP captioning is unavailable. The figure was not saved; check the cached model and retry.') from exc
            store.save_figure(sid, request_id, page, image, caption, printed_caption.strip(),
                              {**trace, **metadata})
            return detail(sid)

    @router.get('/{sid}/figures/{fid}/image.png')
    def image(sid: str, fid: str):
        figure = store.figure(sid, fid, include_image=True)
        if not figure:
            raise HTTPException(404, 'Figure not found in this session.')
        return Response(figure['image'], media_type='image/png')

    @router.post('/{sid}/figures/{fid}/review')
    def review(sid: str, fid: str, body: FigureReview):
        with session_lock(sid):
            figure = store.figure(sid, fid)
            if not figure:
                raise HTTPException(404, 'Figure not found in this session.')
            run = store.run(sid)
            if run and (run['finished'] or run['active_figure_id'] == fid or
                        any(source.get('id') == 'FIGURE-' + fid for trace in store.traces(sid)
                            for source in trace.get('sources', []))):
                raise HTTPException(409, 'This figure has already entered the conversation; its description is fixed for evidence.')
            store.review_figure(sid, fid, body.text)
            return detail(sid)

    @router.post('/{sid}/figures/{fid}/discuss')
    def discuss(sid: str, fid: str):
        with session_lock(sid):
            figure = store.figure(sid, fid)
            run = store.run(sid)
            if not figure:
                raise HTTPException(404, 'Figure not found in this session.')
            if not figure['reviewed_caption']:
                raise HTTPException(409, 'Review and save the figure description first.')
            if not run or run['finished']:
                raise HTTPException(409, 'Start an unfinished topic practice before discussing a figure.')
            if run['active_figure_id'] == fid:
                return detail(sid)
            if sum(message['role'] == 'student' for message in store.messages(sid)) >= 8:
                raise HTTPException(409, 'This practice has reached eight responses; finish and reflect.')
            store.select_figure(sid, fid)
            return detail(sid)

    @router.post('/{sid}/figures/return-to-topic')
    def return_to_topic(sid: str):
        with session_lock(sid):
            run = store.run(sid)
            if not run or run['finished']:
                raise HTTPException(409, 'Start an unfinished topic practice first.')
            if not run['active_figure_id']:
                return detail(sid)
            store.select_figure(sid, None)
            return detail(sid)
