# Feynman Buddy

A local study buddy for learning by teaching. **Checkpoint 0.2: PDF notes and grounded text practice.** This new project is separate from the earlier reference-point prototype.

## What works now
- Create a named, one-topic study session.
- List, open and reload saved sessions.
- Store sessions in local SQLite across backend restarts.
- Handle invalid names, missing sessions and connection failures.
- Upload one selectable-text PDF per session (up to 10 MB and 20 pages), preview extracted passages and open the source pages.
- Prepare a persistent MiniLM retrieval index without requiring numbered headings or statement selection.
- Start teaching the local buddy, send up to eight short explanations and generate a source-linked reflection.
- Restore the conversation after restart and export the conversation, source passages and experimental traces.

Voice and diagram interpretation are not implemented in this new build yet. The text model is provisional: a live development test showed answer leakage and imperfect reflection categories. Responses can take tens of seconds on this CPU; reflections may take minutes. This is not validated grading or instant voice conversation.

## Start on this computer
Open two PowerShell terminals in this project folder:

```powershell
.\scripts\start-backend.ps1
```

```powershell
.\scripts\start-frontend.ps1
```

Open http://127.0.0.1:5174 . API documentation: http://127.0.0.1:8001/docs . Different ports keep this separate from the old prototype.

Ollama must be running locally with `qwen3.5:4b` installed, and MiniLM must already be cached. The existing machine has both. `STUDY_MODEL` may override the default for a new session. After backend code changes, stop it with Ctrl+C and run its start script again. The UI cannot add new endpoints to an already-running old backend.

For initial setup, `.local/runtime.json` points to the existing Python environment and `frontend/node_modules` is a directory junction to existing frontend dependencies. No model downloads are needed at this checkpoint. Do not delete the old environment yet. Application source and SQLite data belong to the new project. Do not install/update shared dependencies through the junction; create independent dependencies first if versions need to change.

## Independent environment / repository setup
The local runtime file, dependencies and private data are excluded from Git. On a fresh checkout:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
cd frontend
npm ci
```

On this computer, replacing shared dependencies requires removing ONLY the dependency junction using a non-recursive link-removal operation before installing locally. Do not recursively delete its target. Update/remove `.local/runtime.json` when switching to the independent Python environment. Planned model dependencies are listed separately in `backend/requirements-models.txt`; model caches are not source files. Requirements record direct versions tested on this machine, not a full cross-platform environment lock.

Git has not been initialised, committed or pushed by this setup. Never commit private uploaded notes, recordings, session databases, keys or installed models.

## Code map
- Optional diagram practice: after uploading notes, open “Start a separate diagram practice”, upload a cropped PNG/JPEG and specify its PDF page. Review/save Granite's description, then start. The new session has its own conversation and reflection. Install `granite3.2-vision:2b` in Ollama once; it is already installed on the development machine. Image analysis can take minutes on CPU. Restart the backend after this update.
- `backend/app/diagram_routes.py`, `services/vision.py`, `frontend/src/DiagramPractice.jsx`: separate diagram practice. See `docs/diagram_implementation.md` for evidence and limitations.
- `backend/app/main.py`: API routes and lifecycle.
- `backend/app/schemas.py`: validated API inputs/outputs.
- `backend/app/storage.py`: SQLite operations.
- `backend/app/study_routes.py`: document/practice lifecycle and safe retries.
- `backend/app/services/documents.py`: PDF text extraction and page-linked overlapping passages.
- `backend/app/services/inference.py`: local embedding, retrieval, conversation and reflection calls.
- `frontend/src/App.jsx`: session creation and study-space interface.
- `frontend/src/StudySession.jsx`: PDF upload, source preview, conversation and reflection.
- `frontend/src/api.js`: network boundary.
- `prompts/`: versioned prompts when implemented.
- `evaluation/`: candidate comparisons and final evaluation protocol.
- `docs/`: decisions, requirements, tests and report evidence.

## Test
From `backend`, use the configured Python interpreter:

```powershell
python -m unittest discover -s tests -v
```

From `frontend`: `npm run build` and `npm run lint`. Backend tests use temporary databases and mock inference boundaries; they verify software behaviour, not model accuracy. `evaluation/run_text_smoke.py` runs a separate real-model development check; its results are not held-out evaluation.
