# Agreed direction and submission coverage

Status: the intended scope below was recorded during redesign. The new text conversation pipeline is now implemented; audio and image integration remain outstanding. See current_design_audit.md for the verified current status. Historical checkpoint wording below does not override that audit.

## Template identity
CM3020 Artificial Intelligence, 4.1 Project Idea 1: Orchestrating AI models to achieve a goal. Use this identity in the CM3070 final report; do not confuse the project-template subject number with the final-project module number.

## Purpose and scope
A local Feynman practice buddy lets a student create a named one-topic session, upload selectable-text PDF notes, teach the buddy through text or recorded speech, receive grounded conversational follow-ups and finish with a source-linked practice reflection. This is formative practice, not validated mastery grading or proof of improved learning.

No mandatory numbered headings, automatic topic discovery, reference-point selection, all-reference checking per turn, rigid Bloom progression or composite mastery score. The session name sets the topic. Preserve human correction of transcripts and image descriptions. Support simple selectable-text PDFs initially; unsupported scans or broken extraction require a clear message rather than silently proceeding.

## Model orchestration requirement
The supplied template explicitly requires at least THREE pretrained models operating in different domains/data spaces and an integrated working purpose. Planned roles:
- Audio: Whisper transcribes the learner explanation to editable text.
- Image: BLIP is the current image-description candidate. Reviewed figure descriptions enter the same retrievable notes as PDF text, retaining page and image identity. Its weak diagram output means suitability is not established; evaluate factual correctness and correction burden, and compare an alternative if feasible.
- Text: a local Ollama LLM generates grounded conversational follow-ups and an end-of-session reflection.
- Supporting text retrieval: MiniLM embeddings index and retrieve session passages.
Local speech synthesis provides spoken output but is not relied upon to meet the three-model requirement. Multiple calls to the same LLM are not counted as multiple pretrained models. Removing NLI from the conversation does not remove the required audio/image/text coverage.

The integrated image demonstration must use information actually present in a diagram, retrieve the reviewed description in a relevant exchange, and preserve the image/page link. A disconnected caption button is not enough. Report the unedited caption and the human correction separately. If caption quality is poor, disclose that limitation; do not describe human-written content as model success.

## Proposed processing path
Create named session -> upload notes -> extract text/images with page provenance -> chunk and index text plus reviewed image descriptions -> start conversation. Retrieve relevant session context before a generated opening and on each learner response. A fixed greeting may precede retrieval without needing inference. One local LLM call per ordinary turn receives instructions, topic, bounded dialogue history and retrieved context. Store full dialogue and source IDs. The system validates source IDs and renders model text safely. Finish triggers a separate grounded reflection that distinguishes learner assertions, corrections, hints supplied by the buddy and topics not discussed. Text and speech replies are not implemented in the copied redesign yet.

Persist local sessions, messages and document metadata in SQLite. Keep uploaded files and indexes under application data directories excluded from the public repository. Queries must be scoped by session/document IDs. Model instructions treat notes and user explanations as data, not commands. Limit upload size and generation resources. Keep these engineering checks; removing the old pedagogical controller does not mean removing error handling or isolation.

## Bloom's taxonomy boundary
Retain Bloom's in the literature review and use it as a rationale for varied follow-ups, especially understanding, application and analysis. Example gradient-descent questions: explain why subtracting the gradient helps; compute one update; explain the effect of increasing the learning rate. These examples are proposed prompt behaviours, not demonstrated learning gains or validated taxonomy labels.

No six-stage ladder, no classification of a student's ability into a Bloom level, and no claim that a question's verb alone establishes its cognitive level. Human review can assess whether generated questions elicit explanation, application and reasoning in context. If comparing prompt variants, use the same model and cases and report conversational quality, errors and latency. SOLO can remain relevant literature with an explicit statement that automated SOLO scoring is not implemented.

Educational reference: Iowa State University CELT, Bloom's Taxonomy, https://celt.iastate.edu/prepare-and-teach/design-your-course/blooms-taxonomy/ . Obtain complete bibliographic citations and consult original literature when revising the literature review; this web reference does not replace the existing academic sources.

## Template evidence map
| Brief requirement | Planned implementation/evidence | Current status |
|---|---|---|
| Well-specified domain problem | Self-explanation practice grounded in personal study notes | Scope defined |
| Three pretrained models across data spaces | Whisper audio, image-caption model, conversational LLM; MiniLM supports retrieval | Models exist in baseline; redesigned integrated flow pending |
| Working integrated product | Named session, upload, spoken/typed explanation, retrieval, dialogue, reflection | Baseline exists; replacement flow pending |
| Model identification and operationalisation | Model/version manifest, input/output formats, prompts, chunking and integration rationale | Existing evidence to retain and update |
| Testing/rejecting model candidates | Preserve NLI/Llama/Qwen development runs; conduct fair relevant comparisons | Historical runs exist; not a controlled leaderboard |
| Performance appropriate to use | Stage timings, cold/warm latency, first text/audio and complete response | Slow baseline measured; redesign timing pending |
| Software quality | Modular services, tests, failures, source provenance and session isolation | Baseline tests exist; new-flow tests required |
| User interaction and iteration | Actual learner tasks, usability observations, grounded dialogue rubric | User feedback exists; formal observations pending |

## Final report requirements supplied by the student
The final submission has six chapters and a STRICT total maximum of 10,500 words. Individual maxima remain binding; their sum is not permission to exceed the total.

| Chapter | Maximum | Working target |
|---|---:|---:|
| 1 Introduction | 1000 | 850 |
| 2 Literature review | 2500 | 2100 |
| 3 Design | 2000 | 1700 |
| 4 Implementation | 2500 | 2300 |
| 5 Evaluation | 2500 | 2400 |
| 6 Conclusion | 1000 | 650 |
| Total | 10500 | 10000 |

Targets are a drafting allocation, not measured current counts. Count actual prose before submission. The supplied guidance excludes reference lists, table/figure legends and chapter titles; do not assume ordinary prose in tables is excluded. Additional image/reference pages are allowed.

Chapter 1 states the exact project-template number and purpose. Chapters 2-3 revise existing work with feedback and actual design changes. Chapter 4 explains major algorithms/techniques, carefully selected code excerpts and screenshots/results for the whole implementation. Chapter 5 explains actual evaluation procedure, justification of analysis, results, successes, failures, limitations and extensions. Chapter 6 draws conclusions supported by findings.

Topic 6 is style guidance for Implementation, not its final word limit. The intermediate task had a 2000-word maximum, minimum 12-point font and 2 cm margins; the final Implementation chapter permits 2500 words. Retain readable 12-point/2 cm formatting as a practical baseline and check any additional final-format instructions.

## Assessment coverage checklist
- Clear writing, diagrams and presentation: one consistent glossary and diagrams matching implemented code; readable screenshots with captions.
- Literature knowledge and critical evaluation: relate Feynman practice, grounded dialogue and questioning to academic evidence; compare strengths and limitations rather than listing papers.
- Citations: proper references for external claims, models, datasets and educational theory; no invented references.
- Design and user/domain justification: tie each feature to a stated learner need and explain constraints and trade-offs.
- Implementation quality and technical challenge: show multimodal data transformations, retrieval, inference, persistence, provenance, error handling and voice integration through explained code excerpts.
- Evaluation relevance and coverage: component tests plus complete sessions, model errors, retrieval, speech, images, latency and usability. Separate mocked software verification from model evaluation.
- Results and critical analysis: raw saved runs, explicit sample sizes/denominators, failures and comparison against aims. Do not infer learning gains from a short usability exercise.
- Conclusions and discussion: explain what evidence supports, where scope narrowed and realistic extensions.
- Originality: explain the project's integration and interaction contribution; do not claim invention of RAG, Feynman practice or pretrained models.
- Video: show an actual working integrated system and explain its operation and limitations clearly within the permitted duration.

## Repository and video obligations
Include a publicly viewable repository link in the report; it must remain viewable until results are received. Prepare code, dependency instructions, sample material and documentation first. Exclude private notes, recordings, transcripts, secrets, machine-specific identifiers, model weights and installed dependency directories. Publication is a separate explicit action; no repository is published by this preparation.

Submit a 3-5 minute demonstration video with the student's own spoken narration. The supplied rules prohibit AI-generated narration voices and sped-up footage. The student distinguishes application speech from narration and intends to demonstrate the buddy speech feature while personally narrating. This is the student's interpretation; no institutional clarification has been obtained. No video has been recorded or validated yet. Do not fabricate response speed. Plan a realistic demonstration with actual measured latency, showing important integrated features rather than unrelated model demos.

## First implementation checkpoint
1. Build named-session persistence and ordinary-PDF ingestion, retaining page provenance.
2. Implement grounded text conversation and end reflection; remove old checklist logic from the active path.
3. Test one complete gradient-descent conversation: correct explanation, misconception, clarification, self-correction, unrelated response and finish/export. Confirm session reload and source links.
4. Measure response time and question quality before adding more features or changing models.
5. Integrate and test recorded speech, reviewed diagram context and local playback.
6. Freeze configuration for held-out evaluation; collect real screenshots/results and write chapters against the actual build.

Existing software tests and historical benchmark results must not be relabelled as final results for the redesigned system. Keep the original folder intact and work in a separate source copy; reuse installed runtimes/model caches rather than duplicating gigabytes of dependencies.


## Subsequent workspace decision
The user chose a new independent folder/repository, feynman_buddy, instead of a worktree. Checkpoint 0.1 implements persistent sessions only; see decisions.md. The old project is preserved.
