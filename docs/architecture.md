# Architecture by responsibility

## Implemented: checkpoint 0.1
Browser -> React interface -> local /api proxy -> FastAPI validation -> SQLite session store. Each session has a UUID, student-provided name and UTC creation/update timestamps. A URL query parameter selects the current session. Data survives page reload and application restart. No models are invoked yet.

## Checkpoint 0.2: implemented text pipeline
Session upload stores the original PDF, page-linked chunks and normalised MiniLM vectors in SQLite. Chunks are at most 180 words with 30-word overlap within each page; headings are not required. One document per session is frozen after upload to prevent the source changing underneath a conversation. A separate session can use another PDF.

The opening is a fixed invitation using the student's topic. On each submitted explanation, retrieval uses the topic, latest buddy message and student response to select three passages from that session only. One Ollama generation call receives those passages and the last six messages. There is no per-reference classifier, NLI verifier or all-reference state update. Complete dialogue remains persisted even though live prompt history is bounded.

The final reflection receives the full short transcript (maximum eight student messages) and up to six source passages collected from the turn retrieval traces. It generates provisional observations. Student-message and source IDs are checked before evidence cards are displayed; this establishes provenance, not semantic accuracy. The UI combines the model's proposed categories into neutral observations because the first live run misplaced a self-correction into its revisit category. Raw categories remain in the saved trace for evaluation.

Messages and retry identifiers commit together after successful generation. A retry cannot duplicate a turn; model failure leaves the dialogue unchanged. SQLite schema version 2 adds documents, practice runs, messages and turn traces without deleting existing sessions. Source PDF and embeddings persist with the session. Runtime content stays in ignored data directories.

## Prompt and reflection revision
The active prompts are now conversation-v2 and reflection-v2 (D009). Reflection introductions are application-generated factual descriptions, not LLM verdicts. Legacy reflection introductions are suppressed with a version notice; original saved outputs remain exportable. Each new reflection trace records its own reflection prompt version, separately from the conversation version. A practice run's version records its starting configuration; per-turn traces identify the prompt actually used if an unfinished session spans an update.

## Remaining components after the grounding correction
Current coverage is audited in current_design_audit.md. Source passages saved for each generation are now exposed through reply_sources in the study API and a collapsible UI disclosure. Explicit message IDs identify new traces; checked atomic turn order supports legacy traces. No extra generation is needed. Evidence excerpts are also shown in reflection details, without implying that the observation is verified.

- Speech controls are now implemented: recording -> browser PCM WAV -> local Whisper -> editable transcript -> explicit send. Original transcript and edits are associated with the turn. Local voice playback stops on recording. See speech_implementation.md; microphone/playback end-to-end verification remains outstanding.
- Vision: figure -> caption suggestion -> reviewed description -> retrievable context and original image/page link.
- Model/prompt comparison: address latency, multiple questions, answer leakage and reflection quality using recorded development cases before a separate final evaluation.

Session isolation, resource limits, safe rendering and error handling remain ordinary software responsibilities. Uploaded text and learner responses are data, not system instructions. Source-ID validation establishes a link to real material, not that a generated claim is semantically correct.
