# Working report material and evidence log

Status: provisional prose for the CURRENT TEXT implementation, not a finished report. Update after audio, vision, model comparison and final evaluation. Do not describe planned features as complete. Existing Introduction, Literature Review and Design chapters still need alignment with the final build.

## Chapter 4: current implementation draft

The prototype implements a local study session in which a learner names a topic, uploads PDF notes and explains the topic to a conversational buddy. The application uses a React interface, a FastAPI backend and SQLite persistence. A session identifier scopes documents, dialogue and retrieval so that one session's source material is not used in another session. The interface supports inspection of extracted text and access to the original PDF before practice starts.

PDF ingestion uses pypdf to extract selectable text. Each page is divided into passages of at most 180 words with a 30-word overlap. Page identifiers are preserved for later source inspection. This straightforward strategy avoids requiring users to format notes using numbered headings, but may divide a definition across passages and flatten mathematical notation. The upload path rejects unsupported inputs and limits file size and page count. Scanned documents and image understanding are not supported by the current text checkpoint.

The all-MiniLM-L6-v2 encoder converts passages into normalised vectors, stored with their text in SQLite. For each learner response, the retrieval query combines the session topic, the preceding buddy message and the learner's current text. The system ranks passage vectors by their dot product with the normalised query vector and selects three passages. With normalised embeddings, this ranking corresponds to cosine similarity. Brute-force ranking keeps the small per-session index understandable and avoids a separate vector-database service. It does not, by itself, identify when the notes contain no relevant answer.

The retrieved passages, recent conversation and versioned instructions are sent to a local model through Ollama. The current candidate is qwen3.5:4b. One model call produces each conversational response. The opening invitation is fixed text containing the learner's chosen topic; subsequent responses are generated. Instructions encourage explanation, application and reasoning about connections, drawing on the project's Bloom-informed questioning rationale without assigning a cognitive level to the learner. Prompt instructions are behavioural requests rather than enforced guarantees.

Each successful turn stores the learner message, buddy response and retrieval trace in one database transaction. Request identifiers allow a failed network request to be retried without duplicating a completed turn. The complete short conversation persists, although live generation receives only six recent messages. The present eight-response limit is an engineering bound rather than a pedagogical claim about an appropriate practice duration.

At completion, a separate generation call proposes source-linked observations about the learner's contributions. The backend accepts evidence references only when they identify actual student messages and supplied source passages. This validates provenance but does not prove that an observation is semantically justified. An observed failure, where a reflection endorsed an incorrect buddy hint, motivated replacement of the free-form generated summary with a factual introduction. Versioned prompt revisions and raw model outputs are retained for comparison.

Source transparency is exposed through an expandable section beneath each generated reply. It displays the actual passages supplied for that turn, rather than citations invented by the model. The interface explicitly distinguishes supplied context from verified support. Reflection details also show source text alongside learner quotations, allowing the learner to compare the observation with its evidence. These disclosures add no inference call and do not change the conversational sequence.

Suggested code excerpts for the final chapter: services/inference.py retrieve and reply; storage.py save_turn; reflection evidence validation; services/evidence.py source association. Explain each excerpt's purpose and limitation. Add real screenshots after the full interface is stable. Add proper model/software references using verified sources during final citation work.

## Chapter 5: evidence currently available

Update after the initial draft: a controlled generation comparison now exists in local_model_comparison_report.md. It covers 20 calls, two installed candidates and ten fixed synthetic development cases. Insert its method/results/limitations into Chapter 5 and update the provisional model-choice rationale in Chapter 4. This does not complete held-out, retrieval, multimodal or user evaluation. Earlier future-tense comparison planning below is superseded by that record for the first two-candidate experiment.

Separate software verification from model quality. The current backend suite contains 25 passing tests covering session persistence, upload handling, session isolation, retries, reflection evidence identifiers and source-to-reply association. Frontend build and lint pass. These results do not establish factual accuracy, educational benefit or usability.

Development evidence includes the gradient-descent failure and prompt revision, plus one six-response Sets conversation. The Sets trace confirms that source passages were supplied on every turn, but qualitative review found unsupported extension beyond the extracted material, leading questions, evidence-attribution errors and inappropriate criticism of equivalent notation. The six generation times averaged 52.562 seconds and reflection took 104.999 seconds. This indicates a response-time limitation on the current hardware; these observational timings are not a controlled candidate comparison.

Do not report percentages of model accuracy from these qualitative examples. They have been used to guide development and cannot serve as a held-out final test. A fair candidate comparison should hold cases, prompt and retrieval context constant, record output and latency, and review factual support, question quality, hint quality and reflection attribution separately. Final evaluation should use different examples after the configuration is frozen. Claims about improved learning would require a suitable study that has not been conducted.

## Where each record belongs
| Record | Report use |
|---|---|
| Intended behaviour and evaluation criteria | Chapter 3 Design |
| Actual algorithms, modules, UI and implementation trade-offs | Chapter 4 Implementation |
| Candidate comparisons, test procedures, results and limitations | Chapter 5 Evaluation |
| Prompt versions, full case specifications and raw results | Repository/supplementary evidence; cite selected findings in chapters |
| What the implemented system ultimately achieves | Chapter 6 Conclusion, after final evaluation |

## Working rhythm from now on
For each meaningful feature or experiment, record: purpose; exact change; model/prompt/configuration version; test inputs; actual outputs and timing; result; limitation; and which report section it supports. Update this log and the decision record immediately. Polish the chapter prose at stable milestones rather than repeatedly rewriting the whole report after each small edit.

Retain the strict total maximum of 10,500 words and each chapter's individual limit. This working material is not a full submission and its word count has not been checked against the final chapters. The public repository and personally narrated 3-5 minute demonstration remain separate outstanding requirements.
