# Versioned prompts

Active prompts: conversation-v2.txt and reflection-v2.txt. The v1 files are preserved as the earlier baseline. Version 2 adds explicit treatment of fallible buddy messages, conditional source claims, and uncertainty. Bloom-informed variety remains guidance, not a compulsory sequence or learner score.

Reflection v2 requests evidence-linked observations without a generated narrative summary. The application constructs a factual introduction instead. ID validation still does not verify observation semantics. Raw model output is retained for evaluation. Existing saved reflections are not rewritten; the UI flags the earlier version and suppresses its unchecked summary.

The model and sampling settings remain unchanged for this prompt iteration. Run evaluation/check_grounding_regression.py for three targeted development probes. This does not constitute held-out evaluation or a candidate model comparison. Prompt instructions are not guarantees of behaviour.
