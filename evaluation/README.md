# Evaluation

The first controlled local candidate comparison is complete: 20 calls across two installed models and ten synthetic cases. See local_comparison_protocol.md, cases/local_comparison_v1.json, results/local_comparison_v1/ and ../docs/local_model_comparison_report.md. Initial semantic ratings are coding-assistant judgements awaiting student review, not independent human annotations. The model default remains Qwen provisionally; both candidates failed an equivalent-notation reflection case.

Development cases inform candidate model, prompt and configuration choices. Freeze configuration before using separate held-out cases. Save model versions, prompts, source/input IDs, raw outputs, timing, expected labels/ratings and failure analysis. Human-review ground truth and report actual sample sizes.

Compare feasible conversational LLMs, transcription models, image-caption candidates and retrieval settings. Use common task cases and hold prompts constant where possible when measuring model effects. A component with one tested candidate must not be described as a proven best choice.

Historical baseline evidence remains in ../feynman_project/backend/evaluation and the previous workspace evidence ZIP. Those experiments do not validate this redesign. Current development runs are recorded in results/text_smoke.json and results/grounding_regression_v2.json. See docs/sets_development_review.md for the qualitative review of a real Sets session; its raw personal export remains outside the public source tree. None of these cases is a held-out final evaluation.

Add case files and result files only when actual cases/results exist. Keep personal learner data out of the public repository.
