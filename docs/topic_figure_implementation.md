# Integrating figures into the topic conversation

Status: implementation built 28 September 2026. This document records the current code separately from earlier Granite-only diagram sessions. The earlier sessions and raw experiment files remain preserved for evaluation and backward compatibility.

## Actual flow

The student names a topic and uploads selectable-text PDF notes. A figure is optional: they crop a PNG/JPEG from those notes, identify its page and may enter the figure's printed caption. The page mapping is student supplied, not automatically verified. BLIP produces one short description with the cached local `Salesforce/blip-image-captioning-base` model. The UI shows the image and editable description; the original BLIP output and timing remain stored even when the student corrects it. A description must be saved before discussion.

The ordinary buddy conversation can start before or after figure preparation. On each ordinary turn, MiniLM ranks note passages. Reviewed figures may be offered as optional context to Qwen; no figure is forced into every turn. The student can select one explicitly, or an explicit request to explain a figure selects it automatically when exactly one reviewed figure exists. Selection persists the active figure and shows a neutral invitation in the interface **without adding a buddy message**. Subsequent turns send its reviewed description and retrieved note passages to Qwen in the same conversation. The student sees the image throughout this part of the dialogue. Qwen sees text, not the pixels. Returning to the topic clears the active figure but retains all messages. One final reflection covers the entire practice, with figure sources only if they actually entered a turn.

This is model orchestration toward one learning task: BLIP processes image data; MiniLM retrieves text evidence; Qwen conducts and reflects on the dialogue; Whisper can turn speech into the same student-text path. Browser speech playback remains an optional output feature. A caption passed between models is not by itself evidence that the visual interpretation was correct or pedagogically useful.

## Important boundaries

- BLIP's measured caption on the gradient-descent development image was only “a graph with a line going up and down.” A student or evaluator had to add the arrow relationships. This correction is **not** counted as BLIP performance.
- The buddy must distinguish notes from the reviewed visual description. It cannot assert visual details absent from the text; a student's account of the image is not independently verified.
- The figure can be attached during an unfinished practice and is limited to three images per topic session (8 MB and 16 megapixels per image). Images are oriented, stripped of metadata and resized to fit 1280 × 1280 before storage and captioning. The actual image stays locally in SQLite and outside Git.
- Reviewed figure descriptions become immutable while the figure is active or after it appears in a reply's source trace. Before the learner explains the figure, returning to the topic permits another correction. Original captions are never overwritten.
- Retrieval checks the figure's selected PDF page rather than pretending BLIP's generic sentence has a meaningful semantic similarity score. A selected figure is added explicitly as a source labelled “not similarity-ranked.”
- Existing separate Granite sessions still load. New original topic sessions use the integrated BLIP path. This is a compatibility decision, not two equally recommended flows.

## Source map

- `backend/app/services/blip.py`: cached offline BLIP captioning and timing.
- `backend/app/services/vision.py`: image validation/preparation shared with legacy Granite path.
- `backend/app/topic_figure_routes.py`: image upload, review and active-figure transitions.
- `backend/app/storage.py`: schema version 5, session-scoped figures and active figure; prior databases migrate additively.
- `backend/app/study_routes.py`: page-linked candidate figures, selected figure source, one combined reflection.
- `backend/app/services/inference.py` and `prompts/figure-*.txt`: Qwen context and cautious figure-specific instructions.
- `frontend/src/TopicFigures.jsx`, `frontend/src/StudySession.jsx`: visible figure, review and same-conversation controls.

## Verification and report placement

Forty-five backend software tests pass, including image/session isolation, idempotent upload, review requirement, in-place activation/return without extra buddy turns, automatic selection after an explicit one-figure request, candidate context and exclusion of an undiscussed figure from reflection. Frontend production build, lint and four PCM audio tests pass. These verify software flow with mocked model calls; they do not validate AI caption or teaching quality. The later live gradient-descent session and its revisions are documented in `live_gradient_session_review.md`.

A separate development script (`evaluation/run_topic_figure_smoke.py`) completed with real BLIP, MiniLM retrieval and Qwen on the gradient-descent notes. Its JSON records timings, raw replies and traces. The measured stages were: PDF indexing 14.639 s; BLIP image upload/caption 5.226 s; ordinary Qwen turn 81.615 s; figure Qwen turn 69.674 s; final reflection 175.898 s. These are one run each on this laptop, not averages or response-time guarantees. The ordinary turn supplied a gradient-direction fact before the student had explained it, despite the anti-leading prompt. The figure turn used the described opposing directions but pivoted to a question about a negative gradient rather than continuing with the visible figure. The original reflection produced three observations, one of which wrongly credited the student with explaining how subtracting a positive gradient changes a parameter; the student had only described arrow directions. The original result remains preserved.

A versioned figure-reflection-v2 prompt was then evaluated on the **same** synthetic transcript and sources (`evaluation/results/topic_figure_reflection_v2_recheck.json`). Its single observation accurately limits itself to the student's description of arrow directions and A/B height; the prior unspoken positive-gradient claim disappeared. The revised call took 78.097 seconds. This is a development regression check with prompt exposure to the case, not an independent estimate of quality. Both outputs remain available for Chapter 5.

For Chapter 3, revise the figure path and explain why a selected figure is optional within the topic conversation. For Chapter 4, explain model inputs/outputs, additive data storage, review and source provenance. Show the live figure panel beside the dialogue and one expanded source disclosure. For Chapter 5, report measured BLIP/Granite comparison, end-to-end stage timings, answer leakage or unsupported details, and human correction burden. Explicitly distinguish this developer test from held-out cases or user evaluation. No mastery accuracy or learning gain has been measured.

## Remaining evidence limits

The final build has been captured in a local browser, but the report still needs the student's selected screenshots and narrated video. The real-model development runs used gradient-descent material; fresh topics, non-graph figures, real speech recordings and novice learners were not evaluated. A clean-machine installation has not been verified. These gaps should remain explicit in the final report and demonstration.
