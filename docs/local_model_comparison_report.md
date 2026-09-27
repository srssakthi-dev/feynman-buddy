# Local language-model comparison: development results and decision

## Purpose and method
This experiment compares two already-installed candidates for the Feynman Buddy text workflow: llama3.2:latest (3.2B, Q4_K_M) and qwen3.5:4b (the installed metadata reports 4.7B, Q4_K_M). Model tags alone are not reproducible identifiers, so full digests are retained in raw_results.json. Ollama version was 0.34.4. The application default was not changed during this comparison.

Ten synthetic development cases were fixed before execution: seven conversation cases and three reflection cases. Both models received the same source passages, conversation inputs and current versioned prompts. Cases covered correct explanation, misconception, uncertainty, missing source information, off-topic input, two legitimate natural-number conventions, equivalent notation, self-correction and buddy-to-student attribution. These cases were informed by observed failures and are not held-out tests. No model training or fine-tuning occurred.

The actual application inference functions were called directly. Supplying fixed source passages isolates generation and reflection from retrieval; it does not measure PDF extraction, passage-retrieval accuracy, browser latency or the complete RAG pipeline. A context-sensitivity pair changed only whether the notes' natural-number convention included zero. Both models followed both conventions; this is limited behavioural evidence that supplied context affects output, not proof of grounding for all claims. No no-context ablation was run.

Common settings were temperature 0.2, seed 42, non-streaming output, 4096-token conversation context and 8192-token reflection context, with output limits of 160 and 1000 tokens respectively. Qwen thinking was disabled. The two architectures use different tokenizers, so identical messages need not have identical token counts. Runs were sequential, Llama first, with one sample per model/case. The current prompts had previously been refined with Qwen, an acknowledged source of bias. They were not changed during this experiment.

## Completion and latency
All 20 calls completed; all six reflection outputs parsed as JSON accepted by the reflection routine. All generation stop reasons were "stop", rather than output-token exhaustion. Successful execution and parsing do not imply factual correctness or valid evidence references.

| Candidate | Conversation calls | Median / mean conversation seconds | Reflection calls | Median / mean reflection seconds |
|---|---:|---:|---:|---:|
| Llama 3.2 | 7 | 2.860 / 5.211 | 3 | 19.981 / 23.244 |
| Qwen 3.5 | 7 | 22.372 / 23.297 | 3 | 45.522 / 41.958 |

Conversation ranges were 2.091-17.103 seconds for Llama and 18.386-36.346 seconds for Qwen. Reflection ranges were 17.011-32.741 and 29.916-50.435 seconds respectively. These are measured call times for short fixed inputs, not expected response times for every uploaded PDF. They include loading and prompt processing; initial loading, caching, sequential order, model residency and possible shared-server activity limit timing comparability. No controlled cold/warm repetition or time-to-first-token test was conducted.

For the uncertainty case, Llama spent approximately 0.877 seconds processing its prompt and 1.784 seconds generating; Qwen spent 17.701 and 5.196 seconds respectively. This example suggests prompt processing contributes materially to Qwen's delay, but does not establish that reducing prompt length would preserve response quality. Full timing fields are saved.

## Provisional output review
The coding assistant reviewed each output against criteria written before execution. This is not independent human annotation, inter-rater validation or a learner study. The student should review the saved outputs and judgements before using them as final evaluation evidence. Pass means meeting that case's minimum criterion, not verified overall teaching quality. No aggregate educational-accuracy score is calculated.

| Case | Llama raw output | Qwen raw output | Main finding |
|---|---|---|---|
| Correct explanation | Partial | Fail | Llama repeats the goal in a leading question; Qwen gives away new gradient-direction facts. |
| Misconception | Pass | Pass | Both identify the reversed gradient direction. |
| Uncertainty | Partial | Pass | Qwen preserves the step-size caveat; Llama's hint lacks a clear follow-up. |
| Missing source information | Pass | Pass | Both acknowledge that the supplied notes omit the requested formula. |
| Off-topic response | Fail | Pass | Llama judges the unrelated sentence as a set explanation; Qwen invites a link back to the topic. |
| Notes include zero | Pass | Pass | Both follow the supplied convention. |
| Notes exclude zero | Pass | Pass | Both follow the alternative convention. |
| Equivalent notation reflection | Fail | Fail | Llama invents learner contributions; Qwen unfairly requires formal notation/source citation. |
| Self-correction reflection | Fail | Pass | Llama recognises correction but invents source IDs; Qwen correctly cites the later student message. |
| Buddy-attribution reflection | Fail | Pass | Llama cites buddy messages as learner evidence; Qwen records uncertainty without endorsing the false hint. |

Under these provisional criteria, conversation results were Llama 4 pass/2 partial/1 fail and Qwen 6 pass/0 partial/1 fail, out of seven each. Raw reflection results were Llama 0 pass/3 fail and Qwen 2 pass/1 fail, out of three each. These tiny, related, development-only denominators must not be described as general model accuracy estimates. Some passing responses still contain leading or repetitive follow-ups.

## What the software validation did and did not prevent
For Llama's self-correction case, every observation included an invented source ID, "page 1", alongside the valid GD1 ID. The backend rejected all three observations. The application therefore displayed no evidence of the correction even though the raw language recognised it.

For Llama's buddy-attribution case, all four observations cited buddy IDs and were rejected. The resulting empty reflection is an allowed safe outcome for that specific case. Therefore the displayed application outcome passes the narrow safety criterion, while the raw model fails it. This distinction prevents crediting the model for protection supplied by ordinary validation code.

For equivalent notation, both models used valid identifiers with unsupported interpretations. Those observations survived validation. Llama attributed universal-set, union and duplicate-element statements to a learner who had not made them. Qwen criticised a correct explanation for not citing a definition or writing the formal symbol. This demonstrates that reference validation cannot replace semantic evaluation.

## Decision and next implementation boundary
Retain Qwen as the provisional development default; do not switch the application to Llama solely for speed. Qwen provided more useful source-linked reflection on correction and attribution in these cases, while Llama's speed advantage came with serious reflection failures. This is a constrained engineering decision between two installed candidates under one prompt configuration, not a claim that Qwen is the best available model.

Neither candidate has demonstrated reliable conceptual assessment. Equivalent notation and independent-versus-assisted explanation require further targeted development. Avoid further broad architectural changes or adding an untested second verifier. Before final evaluation, address the observed reflection behaviour, test retrieval separately and repeat with longer conversation context. Speech and image integration remain outstanding template requirements. Do not postpone all multimodal work indefinitely while seeking perfect LLM behaviour.

## Report placement
Chapter 3: describe the comparison criteria and separation of development from final evaluation. Chapter 4: describe the chosen model interface/configuration and briefly justify the provisional choice, referring to Chapter 5. Chapter 5: present the method, complete denominators, latency table, representative failures and limitations above. The code repository can contain the synthetic fixtures, full prompts, runner, raw outputs and review records. No personal uploaded notes are included in these fixtures.

Suggested Chapter 4 wording:

"A development comparison used the same seven conversational and three reflection cases with two installed local candidates. Qwen was retained provisionally because it produced more usable source-linked reflection for the correction and attribution cases, although Llama responded faster. Both models failed the equivalent-notation reflection case, so the selection does not establish reliable assessment. The comparison procedure, outputs and limitations are reported in Chapter 5."

## Evidence inventory
- evaluation/local_comparison_protocol.md: protocol fixed before execution.
- evaluation/cases/local_comparison_v1.json: synthetic inputs and acceptance criteria.
- evaluation/run_local_comparison.py: actual inference runner with raw capture before reflection filtering.
- evaluation/results/local_comparison_v1/raw_results.json: all 20 calls, exact messages, raw/cleaned outputs, prompts, model digests and timings.
- evaluation/results/local_comparison_v1/complete_outputs.md: readable complete outputs, including discarded reflections.
- evaluation/results/local_comparison_v1/timing_summary.json: calculated latency summaries.
- evaluation/results/local_comparison_v1/provisional_review.json: explicit assistant-assigned judgements and reasons; awaiting student review.

No existing study session was altered, no application model setting was changed, and no network model download or paid API was required.
