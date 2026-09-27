# Separate diagram practice — implementation and evaluation record

Date: 28 September 2026. Checkpoint 0.4.0. Model choice authorised by the student: Granite vision, using the earlier BLIP experiment as a historical baseline. This record separates software verification, development inference and uncompleted evaluation.

## Implemented flow

1. Upload ordinary selectable-text PDF notes to a topic session as before.
2. Optionally open “Start a separate diagram practice”. Upload a PNG/JPEG screenshot cropped around one diagram and its labels, and identify its source page. This revision uses manual image selection; it does not automatically discover PDF figures. The page association is supplied by the student and is not automatically verified.
3. Validate image bytes, enforce 8 MB/16-megapixel limits, orient it, flatten transparency onto white, remove metadata and resize within 1280 × 1280. Store the processed image used for inference and hashes identifying original/processed inputs.
4. Granite 3.2 Vision 2B produces a description once, using pixels only. Notes are deliberately excluded from this call so a caption cannot merely repeat surrounding prose. The diagram remains visible. The original description, prompt version, generation settings and timings are retained.
5. A separate saved study session is created, with an independent conversation/reflection and a snapshot of the original notes. The parent topic history is not copied. Failed inference creates no partial practice; matching request IDs return the existing practice after a lost response.
6. The student reviews/edits and explicitly saves the description before starting. Both original and approved descriptions remain stored. Once conversation begins the approved description is fixed to keep the evidence consistent. Review does not establish that the caption is correct.
7. The buddy opens with a neutral invitation to explain the diagram. Each turn retrieves three note passages using the topic, previous question, student response and reviewed diagram context. The approved description is always supplied as an explicitly labelled additional source, rather than hoping that similarity retrieval selects it.
8. Qwen receives this text context and recent diagram conversation; it does not receive the image pixels. Diagram-specific prompt guidance asks about visible relationships, allows uncertainty and avoids unrelated topic questions. The usual student/source provenance checks apply to the separate reflection. This is not a validated visual assessment.

Granite is released from memory after description generation (`keep_alive=0`). Image inference does not run on every conversation turn. CPU preparation latency remains a usability concern; no instant-response claim is made.

## Architecture and code map

- `backend/app/services/vision.py`: image validation/preparation, local Granite request, source adapter.
- `backend/app/diagram_routes.py`: upload, independent practice creation, image serving, reviewed-description approval.
- `backend/app/storage.py`: additive schema version 4, diagram provenance and atomic session/notes snapshot.
- `backend/app/study_routes.py`: start gate, diagram-aware retrieval context, existing conversation/reflection lifecycle.
- `backend/app/services/inference.py`: adds diagram-specific prompt instructions when the explicit diagram source is present.
- `frontend/src/DiagramPractice.jsx`: image upload, page selection, displayed image, editable description and original-output disclosure.
- `prompts/diagram-caption-v1.txt`, `diagram-conversation-v1.txt`, `diagram-reflection-v1.txt`: distinct, versioned responsibilities.

The original topic prompts remain conversation-v2/reflection-v2; diagram instructions supplement them. No NLI/reference-point checklist or Bloom ability classification is introduced.

## Evidence recorded so far

- 40 backend software tests passed, including seven new diagram tests with mocked model inference. These cover isolation, atomic failure, retry behaviour, source-page validation, approval, persistence, frozen evidence and context reaching dialogue/reflection. They are not 40 model-quality tests.
- Frontend production build and lint passed.
- The first live Granite request failed because the image plus prompt required 6,722 tokens but the initial context setting was 4,096. The context setting was corrected to the model's 16,384-token limit. This is an observed integration defect, not an inaccurate caption.
- The corrected live request completed in 286.725 seconds. Its output and provisional coding-assistant visual review are saved in `evaluation/results/granite_smoke_v1.json`. It recognised the loss function but incorrectly called A and B two parameters and omitted both arrow directions. It required substantive correction. A single development image is not a benchmark accuracy estimate.
- The user confirmed that the repaired microphone recording/transcription flow worked. This is user-reported integration evidence, not a measured speech-recognition study.

## Historical BLIP comparison

Update: a new BLIP run now uses the exact prepared image from the Granite development test. It returned “a graph with a line going up and down” in 4.120 seconds from model loading through caption generation (11.377 seconds of Python imports recorded separately). See `blip_granite_comparison.md` and `evaluation/results/blip_matched_diagram_v1.json`. This is one matched-image case, not recovery or replication of the reported 40-image experiment. Both raw captions required correction for the intended directional exercise; Granite superiority is not established.

The student reports testing BLIP on 40 images from one chapter PDF and finding its descriptions basic and unhelpful. The complete PDF/image set and 40 corresponding outputs have not yet been located in the inspected project folders. Do not present 40 individually inspected results or calculate a success rate from that recollection.

One independently recoverable old result is `feynman_project/backend/evaluation/results/live_caption.json`: “a graph with a line going up and down”, 4.530 seconds, explicitly not human-rated in its saved record. The old code uses `Salesforce/blip-image-captioning-base`, unconditioned image captioning with `max_new_tokens=40`. This alone does not establish the settings of every earlier trial or prove the exact matching image.

Use the old experiment as a documented rejected baseline. For a paired comparison, recover the original images and captions and apply Granite to the same selected images. There is no need to rerun BLIP if its outputs and inputs are recoverable. Preserve the BLIP 40-token versus Granite 300-token allowance and different prompting as comparison limitations; this is a comparison of implemented configurations, not an isolated architecture experiment. If different images are used, report illustrative cases rather than a controlled head-to-head result.

Suggested human review fields per image: correctly recognised labels/entities; correctly described relations/arrows; unsupported claims; useful information beyond the printed caption; correction required; processing time. Define scoring before reviewing the comparison and preserve original outputs. Report corrected-caption usefulness separately from raw model quality. One chapter is a narrow sample, not 40 independent subject areas.

## Report placement and figures

Chapter 3: revise the image branch to manual diagram selection → Granite description → review → separate diagram practice. Explain why topic and diagram conversations are separate and why captions are not ground truth.

Chapter 4, proposed section 4.9: describe the implemented flow and model orchestration. Include one short listing from `vision.describe` showing the image-bearing local request; explain fixed decoding settings, once-per-diagram processing and memory release. Include a second short listing only if needed, showing the approved diagram source added to retrieved notes in `study_routes.py`. Avoid repeating complete endpoint/database code.

Figure: show the actual diagram, editable generated description and review button on one screen. A second screenshot can show a diagram-specific question and expanded supplied sources. Clearly identify synthetic developer demonstrations; do not imply a user study.

Chapter 5: report the recovered BLIP baseline, measured Granite outputs, human correction burden and preparation/dialogue latency. Keep model-quality evidence separate from the software tests. State missing evidence and any weak captions. No success rate, learning gain or superiority claim is justified yet.

## Sources

Official model description and supported context: https://ollama.com/library/granite3.2-vision

Local chat API and keep-alive behaviour: https://docs.ollama.com/api/chat

## Remaining checks

Live captioning and the real diagram turn completed. Browser review/save/start was exercised using that recorded caption, with an explicit assistant correction. The caption was reused rather than generated twice; this fixture setup is labelled in the trace. The real turn correctly discussed the opposing directions but followed up with a general learning-rate question, showing imperfect adherence to diagram-only focus. Test the application after backend restart. Recover the historical chapter PDF/output mapping before a paired comparison. A clean installation, broader caption quality evaluation and user study remain outstanding.

## Completed development flow result
The real Qwen turn completed in 46.378 seconds and its reflection in 97.141 seconds. The reflection cited the actual synthetic student message and the reviewed diagram/source notes. It repeated the direction observation twice and described consistency with the diagram without explicitly qualifying the description's provenance. These are limitations, not a perfect result. Raw evidence is preserved in evaluation/results/diagram_workflow_smoke_v1.json. The UI now explicitly states that reflection uses a reviewed AI description and that the conversation model has not independently inspected the image.

After that run, required diagram context was changed from a synthetic similarity value of 1 to similarity=null with an explicit mandatory-selection field. Reflection always includes the diagram source independently of ranking. This corrects trace semantics; it does not change the caption or rerate the recorded live run. The raw run is retained with its earlier trace value. Software regression tests cover the revised path.
