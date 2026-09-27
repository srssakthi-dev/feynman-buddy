# Sets session: qualitative development review

This review uses one actual user-provided development conversation and its saved local export, inspected on 27 September 2026. It is not a held-out benchmark or formal user study. The raw export is retained privately outside the public source tree; do not publish the uploaded notes or identifiable conversation without reviewing permission.

## What the trace establishes
Model qwen3.5:4b; conversation-v2 and reflection-v2. Four PDF pages produced six text passages. Every one of the six generated replies received the same three passages (in different ranking orders): two from page 1 and one from page 2. Pages 3 and 4 were not retrieved for these turns. The reflection used the source passages collected from those turns.

This establishes that note text was supplied to generation. It does not establish that every assertion was derived from or supported by the notes. The extracted passages discuss set definitions, duplicates, equality, set-builder notation, universal sets and the empty set, but do not define union/intersection. The model nevertheless introduced and assessed union/intersection without distinguishing supplementary knowledge. The current pipeline does not interpret diagrams, so visible diagram information cannot be assumed to have reached the model.

## Conversation and reflection findings
| Observation | Assessment |
|---|---|
| Reordering red and blue | Appropriate application of the student's stated unordered-set definition. |
| Buddy introduces duplicate invariance | Gives away a fact instead of eliciting an explanation. Later reflection credits this to the student, although the cited responses did not explicitly demonstrate that property. The student's word 'unique' does not establish an independent explanation of duplicate invariance. |
| Union/intersection discussion | Mathematical distinction is relevant, but direct definitions are absent from the available extracted reference text. The app must distinguish topic relevance from note support. |
| Buddy asks for set-builder notation; student lists elements | Student's union and intersection results are correct in roster notation. The buddy does not acknowledge the difference between the requested notation and the submitted notation. This is a conversational follow-through issue, not proof of conceptual failure. |
| Buddy computes intersection before learner's next reply | Learner then supplies the correct results, but this is assisted practice. Reflection should not treat that as wholly independent evidence. |
| Reflection cites only the two input sets for computed union/intersection | Evidence alignment is weak: the actual computed results occur in a later learner response. The citation does not establish the claimed calculation. |
| Reflection criticises 'upside-down U' | Unfair: the student explicitly identified the symbol and correctly gave the shared element. Inability to type a symbol is not evidence of a conceptual gap. |
| 'Neither set' answered as empty | Depends on a universal set that was never specified. If U={1,2,3,4,5,6}, neither is empty; if U={1,2,3,4,5,6,7}, neither is {7}. Buddy should ask for U before endorsing a result. Its later qualification is useful, but 'makes sense for specific sets like yours' initially assumes missing context. |
| Reflection says student did not consider U | Should be more cautious: the learner had no opportunity to answer the buddy's final question. Record an unresolved question, not a diagnosed lack of understanding. |
| Venn-diagram claim linked to extracted page 2 | The passage mentions diagrams and U but does not describe the outer box and inner circles. Correct general knowledge can still have weak support from the cited extracted passage. |

## Source/extraction caveats
The extracted power-set size appears as '2n' rather than 2 to the power n. Compare the original PDF before deciding whether this is extraction loss or a source issue. Also, the extracted universal proper-subset statement for the empty set conflicts with its own nonempty-set qualification when S is empty. The audit did not visually inspect the original page, so it does not attribute this to the source author or extractor. Source-grounded evaluation is limited by source and extraction quality.

## Timing
Recorded generation wall times for the six replies were 53.846, 51.823, 50.255, 50.243, 50.804 and 58.399 seconds: mean 52.562 seconds, range 50.243-58.399. Reflection generation took 104.999 seconds. These are saved inference-call times, not complete browser latency; they include local model processing and potentially waiting for the inference lock. They are observational timings, not controlled cold/warm benchmark results. This delay is incompatible with a claim of instant spoken dialogue.

## How to test grounding next
1. Retrieval: human-label expected source passages for questions, and measure recall at three plus irrelevant retrievals. Include questions absent from the notes.
2. Grounded generation: review each substantive claim against supplied passages. Report unsupported claims separately from mathematically false claims.
3. Context sensitivity: use paired synthetic notes with legitimate differing conventions, such as whether natural numbers include zero, and verify that the same question follows the supplied convention. Include a no-context comparison. Do not intentionally plant false facts in student-facing notes.
4. Evidence attribution: include cases where only the buddy states a fact, where the student paraphrases after a hint, and where the student independently corrects an earlier error.
5. Reflection: review whether each observation is supported by the quoted student messages and cited passages; accept equivalent notation; do not penalise unasked or unanswered topics.

These tests provide behavioural evidence of grounding, not access to the model's internal reasoning. Keep this Sets example in the development set because it is now used to guide changes.
