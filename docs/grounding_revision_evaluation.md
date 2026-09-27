# Grounding and reflection revision: development evidence

Date: 2026-09-27. This is a targeted development iteration, not a held-out evaluation, learning-gain study or model leaderboard.

## Observed failure
The student explained gradient descent's purpose, then replied "im not very sure" to a leading buddy question. The buddy claimed moving opposite the gradient was "guaranteed" to go down. The notes explicitly state that a large learning rate may increase loss and that improvement at every step is not guaranteed.

The original reflection repeated the claim: "moving opposite the gradient ensures descent, aligning with the source notes". That is false certification of a model-generated hint. The observation that the student expressed uncertainty is reasonable; neither the hint nor a lack of subsequent explanation establishes that the uncertainty was resolved.

## Change and rationale
Keep the session/upload/retrieval/conversation/reflection architecture. Preserve conversation-v1 and reflection-v1 as baseline files. Introduce conversation-v2 and reflection-v2 with general, topic-independent instructions to preserve source conditions, treat buddy statements as fallible, offer small hints after uncertainty, and avoid inferring learning from assistance. No gradient-specific answer rules were introduced into the application prompts.

Remove the unchecked model-generated reflection summary from the display path. Construct a factual introduction counting student responses instead. Continue to show source-linked observations with a caution: valid evidence IDs establish provenance, not semantic correctness. Earlier saved results remain unchanged and exportable; the UI flags their version and suppresses their old unchecked summary. This removes a failure channel rather than proving that the remaining observations are accurate.

## Controlled live probes
Script: evaluation/check_grounding_regression.py. Raw results: evaluation/results/grounding_regression_v2.json. Model: qwen3.5:4b, thinking disabled, temperature 0.2, seed 42. Conversation context 4096, maximum output 160 tokens; reflection context 8192, maximum output 1000 tokens. All three extracted benchmark passages were supplied directly. Retrieval was bypassed to isolate generation; do not describe this as a complete RAG integration test. One run per probe, on a known development example.

| Probe | Observed result | Generation wall time |
|---|---|---:|
| Follow-up to the initial explanation | Still introduced uphill/subtraction in a leading question. Failure remains. | 41.342 s |
| Hint after uncertainty | Avoided an explicit guarantee and asked about rolling too fast. Still imprecise: "should decrease" lacks an explicit small-step condition, and physical speed is not a precise explanation of learning rate. Partial improvement only. | 7.195 s |
| Reflection given the ORIGINAL false buddy hint | Did not endorse or repeat the false guarantee. Recorded student uncertainty and linked source passages. Some observations redundantly paraphrased the initial explanation and attributed parameter adjustment more explicitly than the student actually said. Partial improvement; interpretation remains fallible. | 73.918 s |

These timings are individual CPU runs, not a latency benchmark. Warm-up, model residency and differing prompt lengths prevent treating the second call's shorter time as a measured speed improvement. No comparative v1 rerun was performed; the baseline is the user's observed exchange, so no causal accuracy uplift can be claimed.

## Software verification
20 backend unit/workflow tests passed. New tests verify that an arbitrary generated summary cannot enter the displayed reflection introduction, raw output remains available, the reflection prompt version is recorded, and buddy-only evidence cannot become a student evidence card. Frontend production build and lint passed. These checks establish software behaviour, not model factual accuracy. No new browser interaction test was performed for the small legacy-summary display change.

## Next evaluation boundary
Compare a small set of available local candidate models under the same task, source passages and prompt. Human review should separately score factual grounding, leading questions, hint appropriateness, reflection attribution, recognition of corrections and latency. Add unrelated-topic cases and cases with missing source information. Tune only on development cases, then freeze configuration before a separate held-out set. Treat uncertainty as a request for support, never as a whole-topic failure. Bloom-informed question variety remains a design rationale, not an automated learner-level assessment.

## Running the revision
Restart the backend with scripts/start-backend.ps1 and refresh the frontend. Start a new session for a clean v2 run. Finished earlier sessions are preserved and do not regenerate automatically. If the frontend is a development server it normally reloads changed files; restart it with scripts/start-frontend.ps1 if needed. Existing session starting-version metadata is historical; per-turn and reflection traces identify actual generation versions.
