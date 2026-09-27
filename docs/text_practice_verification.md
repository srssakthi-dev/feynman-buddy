# Text practice checkpoint 0.2

Implemented after user testing identified that the initial session screen offered no upload or practice actions. The student-facing path now includes PDF upload, source preview, start, typed replies, finish/reflection and export. It does not require a heading template or reference-point selection. Voice and image interpretation remain unimplemented in this new project.

## Software verification
18 unittest cases passed. The original 6 session tests remain; 12 further tests cover real PDF reading without numbered headings, unsupported PDFs, document immutability, session isolation, idempotent start, transactional model failures, persistent retry records, finish/export behaviour, validation of reflection provenance and preservation of an existing schema-version-1 session during upgrade. Model calls in these software tests are mocked. Build and frontend lint passed.

Temporary live servers used 8101/5184 and an ignored .local/smoke-data database, leaving the user's VS Code processes and actual study database untouched. The production backend needs a restart to load new routes and apply the additive schema update.

## Actual model development run
See evaluation/results/text_smoke.json and the reproducible runner. Two-page project-authored gradient-descent notes yielded 3 page-linked overlapping passages. A fixed greeting began the practice. Real cached MiniLM and Ollama Qwen 3.5 4B processed three explanations and a final reflection.

Observed reply times: 63.64, 28.97, 28.47 seconds. Reflection: 127.08 seconds. These are one run's observations, not a reliable latency distribution. The trace preserves model-load, prompt-processing and generation durations, token counts and retrieved sources.

The model responded to the direction misconception but supplied the answer rather than probing first. It sometimes asked more than one question and used generic praise despite prompt instructions. The final summary recognised the correction, but the model placed both the initial error and correction in revisit and left explained empty. This is not a fully correct pedagogical result. The display therefore presents neutral source-linked observations rather than using these categories as learner judgements. The original output is preserved.

No held-out accuracy, educational benefit or complete user study is claimed. Next quality work should compare candidate models and shorter prompts on complete development conversations, retaining these failures. Latency, answer leakage and correction handling are priorities. Do not relabel this run as independent final evaluation.

## Browser verification
The real file chooser selected the benchmark PDF, Upload and prepare notes completed, Start Feynman practice displayed the greeting, and Send explanation returned a real local model response. No console errors were present at the inspected point. The migration test initially left a fixture SQLite connection open on Windows; closing that fixture connection fixed cleanup, and all 18 tests passed. Temporary test servers were stopped after verification; the user's VS Code servers were not stopped.
