"""Local session API with page-linked notes and grounded teaching dialogue."""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from app.config import DATABASE_PATH
from app.schemas import SessionCreate, StudySession
from app.storage import SessionStore
from app.study_routes import create_study_router


def create_app(database_path: Path = DATABASE_PATH) -> FastAPI:
    store = SessionStore(database_path)

    @asynccontextmanager
    async def lifespan(_app):
        store.initialise()
        yield

    app = FastAPI(title="Explaino", version="0.5.0", lifespan=lifespan)
    app.include_router(create_study_router(store))

    @app.get("/api/health")
    def health():
        return {"status": "ok", "version": "0.5.0", "checkpoint": "topic-figure-conversation"}

    @app.get("/api/sessions", response_model=list[StudySession])
    def list_sessions():
        return store.list()

    @app.post("/api/sessions", response_model=StudySession, status_code=201)
    def create_session(body: SessionCreate):
        return store.create(body.name)

    @app.get("/api/sessions/{session_id}", response_model=StudySession)
    def get_session(session_id: str):
        session = store.get(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Study session not found.")
        return session

    return app


app = create_app()
