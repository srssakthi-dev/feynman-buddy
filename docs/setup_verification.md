# Initial setup verification — 0.1.0

Date: 27 September 2026. Target: new feynman_buddy project. No Git repository was initialised or pushed. Previous project source was not modified.

Implemented: named sessions, normalised input, SQLite persistence, session list/open/reload, initial React UI, local API proxy, launch scripts and documentation. PDF ingestion, embeddings, LLM dialogue, speech, diagrams and reflection are not implemented in this checkpoint.

## Executed checks
- Six unittest API/storage cases passed using real temporary SQLite databases: create/get/list; persisted data across separate app lifespans; invalid inputs; distinct sessions with the same topic; unknown ID; SQL-like name treated as data.
- Vite production build passed with 17 transformed modules.
- Frontend lint completed successfully (exit code 0).
- Actual backend and frontend launch scripts started successfully on 127.0.0.1:8001 and 127.0.0.1:5174.
- Browser created a Gradient descent session, displayed it, then restored the same session after refresh. One demonstration session remains in ignored local data.
- Initial frontend build failed because Vite tried to write temporary configuration beside shared dependencies. Fixed by native config loading and a cache directory inside this project's .local folder. Production build then passed. Shared dependency paths are not application source and must not be installed/updated through the junction.

These checks establish a software setup checkpoint only. No model accuracy, conversational quality, new-model latency or learning outcomes were tested. The old model experiments remain historical baseline data.

## Session navigation correction
User testing found selecting a session appeared ineffective because it only changed an adjacent panel. Replaced that interaction with a distinct session page and an All study sessions control. Browser link activation and browser Back verified. Frontend build and lint passed. Notes and conversation remain clearly marked unavailable in this initial build. Agent preview processes were stopped so the user can launch the app from VS Code.
