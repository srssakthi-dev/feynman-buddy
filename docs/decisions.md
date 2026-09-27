# Decisions

## D015: matched BLIP development comparison
At the student's request, run the historical BLIP configuration on the exact prepared image used by the recorded Granite run, verified by image hash. BLIP returned a generic caption in 4.120 seconds excluding Python imports; Granite took 286.725 seconds and supplied more labels but misinterpreted A/B. Neither captured the key opposing arrow directions. Preserve both outputs and settings; retain Granite provisionally without claiming demonstrated accuracy superiority. This is a single configuration-level development case with assistant review, not a 40-image benchmark. See blip_granite_comparison.md.

## D014: Granite and separate optional diagram practice
User selected granite3.2-vision:2b and reuse of the historical BLIP experiment, not a new Qwen-versus-Granite comparison. A manually cropped diagram image creates its own session with a notes snapshot. Granite runs once; the learner reviews the visible description before starting. Original and edited descriptions remain separate evidence. The approved description plus retrieved notes goes to Qwen; topic messages are never copied. Model quality is unverified until actual outputs are reviewed; the reported 40-image BLIP chapter experiment is historical evidence pending recovery of its files. See diagram_implementation.md.

## D013: remove compressed-recording decode dependency
User testing exposed a browser "Unable to decode audio data" failure. Replace MediaRecorder/decodeAudioData conversion with direct AudioWorklet waveform capture and WAV encoding. Flush the final buffer before shutting down capture. Four frontend regression checks and a frontend-encoder/backend-decoder interoperability check pass; real microphone retry remains pending. No transcription/model configuration change. Record this as an observed integration defect and corrective iteration, not an ASR accuracy failure.

## D012: recorded speech with review before submission
Whisper base now receives in-memory PCM audio prepared in the browser, avoiding a new FFmpeg dependency. Transcription is separate from sending; edited text uses the existing retrieval/dialogue path. Store original transcript and edit provenance locally, but not raw audio. Browser playback uses only localService voices and is stopped before recording. Added eight automated tests; real microphone accuracy and audible playback remain unverified. A local checkpoint-load test passed; the attempted synthetic Windows voice fixture stalled and its invalid-file result is preserved. See speech_implementation.md for exact evidence and limitations.

## D011: retain Qwen provisionally after the first controlled comparison
Twenty calls compared the two installed candidates on seven conversation and three reflection fixtures each using fixed current prompts and source context. Llama was faster, but Qwen handled correction and buddy attribution more successfully. Both failed equivalent-notation reflection. Retain the current Qwen default provisionally; do not claim validated assessment or optimal model selection. Full raw outputs, filtering outcomes, timing, case criteria and explicitly assistant-reviewed judgements are preserved. No live sessions or application model configuration were changed. See local_model_comparison_report.md for method, selection limits and report placement.

## D001: separate folder and repository
User selected a new independent project. The old project remains a fallback and experimental baseline. This is a fresh scaffold with temporary reuse of installed dependencies, not a copy of the old grading pipeline.

## D002: conversation first
Named session -> notes -> grounded teaching conversation -> reflection. The user rejected mandatory numbered headings, statement selection and all-reference grading per turn. One LLM call per ordinary turn is planned, not implemented in checkpoint 0.1.

## D003: durable local sessions
SQLite retains session names across restarts. Initial schema stores named sessions only; documents and dialogue will be added through explicit migrations. Runtime data belongs in the ignored data directory.

## D004: model orchestration and evaluation
Maintain useful audio/image/text processing for the template. Do not retain NLI solely to increase model count. Model choices need practical justification and recorded comparisons. CPU latency is an unresolved feasibility constraint.

## D005: educational theory
Bloom's guides question variety, not learner scores or a six-stage ladder. Retain literature discussion, evaluate actual question quality, and avoid unsupported mastery claims.

## D006: initial setup boundary
The user asked for notification after setup. This checkpoint implements persistent sessions, initial UI, tests and documentation only. PDF/RAG/dialogue/speech/diagrams/reflection remain to implement in the new application.

## D007: video interpretation
The student will personally narrate and intends to demonstrate the buddy's speech as an application feature. Do not repeat the earlier blanket instruction to mute all application speech as an agreed requirement. The assignment wording and the student's interpretation remain distinct.


## D008: real upload-to-text-practice flow
User feedback showed another placeholder was not useful. Checkpoint 0.2 connects PDF ingestion, persistent retrieval, one-call typed conversation and final reflection. Source-linked observations are shown without mastery labels. The first live model run exposed answer leakage, multiple questions, category errors and high CPU latency; these are recorded rather than counted as quality successes. Voice/vision integration and candidate comparisons remain subsequent work.

## D010: show retrieval inputs without implying verified answers
The Sets test showed that the learner could not tell which notes were supplied during dialogue. Each generated reply now exposes its actual saved source passages in a collapsible panel. New traces record student and buddy message IDs; older atomic turn pairs use a checked order-based compatibility mapping. Inconsistent legacy histories are not guessed. Reflection details also show source excerpts. This improves inspectability, not model grounding accuracy. A current design audit and working report log distinguish implemented text features from outstanding audio/image integration and empirical validation.

## D009: isolate the reflection from unsupported buddy authority
The user's uncertainty test produced an unconditional descent guarantee, and the reflection incorrectly certified that hint as aligned with the notes. Version 2 prompts explicitly treat buddy messages as fallible context, retain qualifications from sources, and restrict reflection to student contributions. The unchecked generated summary is replaced with a factual introduction. Existing results remain saved for evaluation; the UI flags legacy reflections rather than silently rewriting them. No extra grading model, topic-specific answer rule or taxonomy classifier is introduced. These changes reduce an exposed failure path; generated observations can still be wrong and require empirical evaluation.
