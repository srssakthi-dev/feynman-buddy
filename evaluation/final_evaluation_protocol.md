# Final evaluation protocol — freeze before collecting results

This is a short, feasible plan for Explaino, preserved to show the intended evaluation. Chapter 5 and the saved results distinguish completed checks from work that was not completed. Record results honestly; blank cells are not evidence. The gradient-descent notes and Sets conversation were used during development, so they cannot be relabelled as held-out examples. Model outputs are fallible, and the reflection is not a mastery score.

## 1. Freeze the configuration

Record Git commit, `GET /api/health` version, Ollama model tags, prompt versions, BLIP/Whisper/MiniLM cache identities, laptop specifications and date. Restart the backend after code changes. Run the tests and save counts. Do not silently change prompts or case wording midway; if a failure leads to a fix, keep pre-fix results and run a clearly labelled revised set.

## 2. End-to-end functional trials

Use one previously unused selectable-text topic PDF and one representative diagram crop from it. Do one real practice with no figure, then another with a figure in the original topic session (a fresh session for each trial). Keep total replies within the eight-response limit. Enter an accurate explanation, a plausible misconception, a brief “I'm unsure,” an off-topic sentence and a later correction. For the figure, review its BLIP caption, select it, explain a visible relationship, return to the topic and finish. Reload between two turns to check persistence. Export each session JSON and preserve screenshots of the displayed source material, in-conversation figure and reflection. Do not edit exports after saving.

Check: notes and figure belong to the correct session; reviewed caption and original BLIP output differ only if corrected; selection changes the **same** conversation; the buddy sees relevant PDF passages and the reviewed caption; the original image is visible to the student; the final reflection credits only student contributions and refers to genuine source IDs. Test one deliberately wrong source-page selection to document that the app trusts the student's page mapping; do not count that as caption error.

## 3. Component evidence

| Component | What to record | Limit |
|---|---|---|
| PDF extraction | Page count, readable passages, any flattened notation/scan failure | Extraction is not OCR |
| MiniLM retrieval | For each fixed question, the expected supporting page/chunk chosen before checking results; actual top three and rank | Similarity is relevance, not factual truth |
| BLIP figure description | Raw caption, visible labels/relations captured or missed, unsupported claims, time, amount of human correction | Corrected text is not BLIP success |
| Whisper | Original transcript, manually corrected words, recording duration, transcription time; no raw audio unless the student deliberately preserves a test file | One trial is not a WER benchmark |
| Qwen dialogue | Saved reply, notes and figure context supplied, whether it follows the learner, leaks an answer, invents visual detail, asks a focused question, time | Source visibility does not prove grounding |
| Reflection | Every observation's quoted student message and source, false attribution, repeated observations, missed later corrections, time | Not a learning-gain or mastery score |

For captioning, the prior one-image BLIP/Granite comparison is development evidence. If a second unseen diagram is available, repeat the same visible-fact and correction-burden review with a different diagram type; do not claim a 40-image controlled benchmark unless the old chapter image/output set is recovered.

## 4. Consistent review sheet

For each buddy turn, record: **relevant to the learner?** (yes/partly/no), **supported by supplied sources?** (yes/uncertain/no), **answer leaked before the learner attempted it?** (yes/no), **visual claim not established by caption/notes/student?** (yes/no), and **one clear follow-up?** (yes/no). Quote the exact offending sentence and source passage for any failure. These are coding-assistant or student judgements, not blinded expert labels; identify the reviewer. Do not average them into a learner ability score.

For each reflection observation, use **supported**, **overstated**, or **unsupported** against the quoted student text and linked source. Mark repeated observations separately. Report numerators and denominators only for cases actually reviewed, e.g. “2 of 6 reviewed replies asked a leading question.” Avoid percentages for tiny samples.

## 5. Whole-system judgement

Compare the final behaviour against the goal: does it let a student teach a chosen concept, use their notes, optionally explain a figure, receive a natural follow-up and inspect a provisional reflection? Report both the working path and the costs. On this Ryzen 5 PRO 4650U/16 GB laptop, the recorded development run took 5.226 seconds for BLIP figure preparation, 81.615 and 69.674 seconds for two Qwen replies, and 175.898 seconds for reflection. These are not real-time conversation speeds. Judge whether the student can still use the turn-based interface, and note that spoken output does not make generation instantaneous.

If a volunteer tries the application, obtain their consent and use only data they agree to share in the report. State participant count, tasks and observations; one informal trial is usability feedback, not evidence of improved understanding. The student's own trials can be described as developer testing.

## 6. Report and video evidence

Chapter 3: current architecture and limits. Chapter 4: implemented transformations and a few explained code excerpts/screenshots. Chapter 5: this fixed protocol, raw case counts, both successful and failed examples, measured times and a candid critique. Keep failed prompt/model versions in the archive. The 3–5 minute demonstration should show a real session and the diagram in the same conversation, with the student's own narration; do not speed up the recording or pretend local inference was instant.

Before making the GitHub repository public for submission, review tracked files and every pushed commit for private data or working-only material. Deleting a file in a new commit does not erase old history. Rewriting remote history removes it from ordinary repository history but cannot guarantee that copies already fetched or cached disappear.
