# Explaino

Repository: https://github.com/srssakthi-dev/feynman-buddy

**Explaino** is a local study application for explanation-based practice. A learner uploads notes on one topic, teaches that topic in text or speech, optionally discusses a selected figure, and reviews a source-linked reflection. It implements the **CM3020 Artificial Intelligence template, Section 4.1, Project Idea 1: “Orchestrating AI models to achieve a goal”** for the CM3070 final-year project.

The goal is one connected study activity, rather than separate model demonstrations. Whisper transcribes speech; BLIP suggests a figure description; MiniLM retrieves passages from the learner's PDF; and Qwen, served by Ollama, asks follow-up questions and drafts a provisional reflection. The learner can correct a transcript or figure description before it enters the conversation. Qwen receives reviewed text and retrieved passages, **not the figure's pixels**.

## What an examiner can try

1. Create a named topic session and upload a **selectable-text PDF** (up to 10 MB and 20 pages). Open the extracted-text preview and the original page link. Scanned PDFs without usable text are rejected; OCR is outside scope.
2. Select **Start explaining**. Type an explanation or record up to 60 seconds of English speech. Whisper's transcript is editable and is sent only after the learner chooses to use and submit it.
3. Optionally add a cropped PNG/JPEG figure (up to 8 MB), enter its PDF page number, inspect BLIP's original caption and save a reviewed description. A selected figure remains in the **same topic conversation**. The page number is supplied by the learner, not verified automatically.
4. Inspect a buddy reply and expand **Notes supplied for this reply**. These are the actual passages supplied to Qwen, with links back to the PDF. Their presence does not prove that the reply is factually supported.
5. Finish and inspect the reflection's quoted learner messages and source passages. The reflection is a study prompt, **not a grade or validated measure of understanding**. Sessions persist locally and can be reopened or exported.

Sample material for a development walkthrough is in `evaluation/fixtures/`. The gradient-descent figure is deliberately challenging: BLIP's raw caption misses important labelled relationships, which the learner must correct. A saved, real-model walkthrough and its timings are in `evaluation/results/topic_figure_smoke_v1.json`. Do not treat the sample walkthrough as an independent accuracy test.

## Run locally on Windows

The tested development computer used Python 3.12, Node.js 24, Ollama, Windows, an AMD Ryzen 5 PRO 4650U and 16 GB RAM. Install Ollama, Python and Node.js first. A clean-machine installation has **not** been verified; the dependency versions in `backend/requirements-models.txt` match the tested computer, but are not a complete cross-platform lock.

From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-models.txt
cd frontend
npm ci
cd ..
ollama pull qwen3.5:4b
```

The three other model weights must be cached **once while online** before the application runs offline:

```powershell
$env:HF_HUB_OFFLINE = "0"
$env:TRANSFORMERS_OFFLINE = "0"
.\.venv\Scripts\python.exe -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
.\.venv\Scripts\python.exe -c "from transformers import BlipProcessor, BlipForConditionalGeneration; BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base'); BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')"
.\.venv\Scripts\python.exe -c "import whisper; whisper.load_model('base')"
```

Run Ollama, then open two PowerShell terminals in the repository root:

```powershell
.\scripts\start-backend.ps1
```

```powershell
.\scripts\start-frontend.ps1
```

Open **http://127.0.0.1:5174/**. API documentation is at **http://127.0.0.1:8001/docs**. The app uses local SQLite storage in the ignored `data/` directory. `FEYNMAN_DATA_DIR` can override that path; its older variable name is retained for compatibility. `STUDY_MODEL` can override Qwen for a newly created session. `WHISPER_MODEL_PATH` can point to a different locally cached Whisper base checkpoint. No paid inference API or cloud account is required.

On the original development computer, `.local/runtime.json` points to an existing Python environment and `frontend/node_modules` may be a dependency junction. Both are ignored by Git. Do not delete a shared dependency target when preparing a clean checkout.

## Architecture and code map

```text
React interface
    -> FastAPI session routes
    -> PDF extraction + MiniLM passage ranking
    -> reviewed Whisper text / reviewed BLIP figure description
    -> local Qwen dialogue and reflection
    -> SQLite messages, sources, traces and exported evidence
```

- `backend/app/study_routes.py`: session lifecycle and the integrated turn from learner input to retrieved sources, Qwen reply and saved trace.
- `backend/app/topic_figure_routes.py` and `services/blip.py`: figure upload, image checks, captioning, review and selection in the current topic.
- `backend/app/services/documents.py`: PDF validation, page extraction and overlapping passages.
- `backend/app/services/inference.py`: MiniLM ranking, Qwen generation and reflection evidence checks.
- `backend/app/services/speech.py`: local WAV validation and Whisper transcription. Raw recordings are not retained.
- `backend/app/storage.py`: SQLite persistence, source provenance and retry-safe turn commits.
- `frontend/src/StudySession.jsx`, `SpeechInput.jsx` and `TopicFigures.jsx`: learner workflow and review controls.
- `prompts/`: versioned conversation, figure and reflection instructions. The active general conversation prompt is `conversation-v3`.
- `evaluation/` and `docs/`: fixed cases, raw development runs, decisions, failures and limitations.

Older standalone Granite diagram sessions remain readable for compatibility. New topic sessions use the integrated BLIP figure route.

## Verification and interpretation

```powershell
cd backend
..\.venv\Scripts\python.exe -m unittest discover -s tests -v
cd ..\frontend
npm run lint
npm run build
node --test src/audio.test.mjs
```

The latest check passed **45 backend tests** and **four audio tests**, plus frontend lint and build. Backend tests substitute model responses to check software behaviour; they are **not** evidence that generated captions or tutoring replies are accurate.

The evaluation also includes a matched BLIP/Granite figure example, a small Qwen/Llama development comparison, an integrated real-model walkthrough and a ten-question **synthetic** retrieval set. Those development cases exposed caption omissions, answer leakage, reflection misattribution and long CPU delays. One walkthrough took 69–82 seconds per Qwen reply and about 176 seconds for reflection. The later eight-response session and known-case rechecks are documented in `docs/live_gradient_session_review.md`. Rechecks on exposed cases are regression evidence, not fresh-case reliability estimates.

The fixed retrieval input, recorded ranking and reproduction script are `evaluation/cases/retrieval_fresh_v1_cases.json`, `evaluation/results/retrieval_fresh_v1_results.json` and `evaluation/run_retrieval_fresh.py`. Run the script with the configured Python interpreter after caching MiniLM; it overwrites the recorded result with a new timestamp.

No completed real-speech word-error-rate set, consented learner study or controlled learning-outcome study is included. Explaino is a working, reviewable prototype for practice, not a validated automated assessor.

## Privacy and repository contents

The repository includes source code, tests, prompts, documentation and synthetic/development evaluation material. `data/`, `.local/`, installed dependencies, model caches, uploaded private notes, recordings and secrets are excluded from Git. The user-facing name is **Explaino**; the existing repository URL and the compatibility variable `FEYNMAN_DATA_DIR` retain the earlier project name.
