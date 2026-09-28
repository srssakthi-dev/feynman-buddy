# Current implementation audit

## Update: integrated figure scope, 28 September 2026

Optional figures now attach to the original topic conversation and are described locally by BLIP. The student reviews the description, can select a figure explicitly, and sees it beside the ordinary buddy dialogue. Retrieval page matches can offer a figure, but a suggestion is not forced and has not been shown consistently in real model output. Figure sources enter the same saved traces and final reflection; the old separate Granite sessions remain available for compatibility. A synthetic real-model walkthrough completed with BLIP, MiniLM and Qwen, but exposed a weak BLIP caption, 81.615 s and 69.674 s text-turn latency, 175.898 s reflection latency, a buddy pivot away from the figure, and a reflection observation that attributed an unspoken positive-gradient explanation to the student. The reflection prompt was revised and rechecked separately; see `topic_figure_implementation.md` and `evaluation/results/topic_figure_smoke_v1.json`. The historical table below is the 27 September audit, not the current status.

Audit updated: 28 September 2026. This is the current status record; earlier checkpoint descriptions are historical. Evidence: active application source, supplied project-template brief, existing automated tests and the user's saved Sets session export. The four model paths are implemented; reliability and user benefit remain subject to evaluation. No validated mastery claim is made.

## Template identity and boundary
CM3020 Artificial Intelligence, 4.1 Project Idea 1: Orchestrating AI models to achieve a goal, submitted within CM3070. The brief requires at least three pretrained models operating in different domains/data spaces, an integrated purpose, evidence of model testing/selection and performance appropriate to the use case. Text/image/audio is its example and is this project's chosen scope. Three text models alone would not implement that chosen scope.

## Design-to-code status
| Intended choice | Actual implementation and evidence | Status |
|---|---|---|
| One student-named topic per session | React session page, FastAPI session endpoints, SQLite | Implemented |
| Ordinary notes without numbered headings | pypdf extraction, 10 MB/20-page limits, scan-only rejection | Implemented for selectable text |
| Inspect the extracted source | Original PDF links and page-linked passage preview | Implemented; preview is not editable |
| Session-scoped RAG | MiniLM normalized embeddings; top-three dot-product retrieval; topic + latest buddy + learner response query | Implemented; retrieval quality not benchmarked |
| Grounding visible during dialogue | Collapsible actual retrieval inputs under generated replies | Implemented in this revision; does not verify claim support |
| Conversational practice | One Qwen/Ollama call per learner response, six recent messages | Implemented; leading questions and answer leakage remain |
| Bloom-informed variety | Prompt invites explanation, examples/application and connections | Prompt guidance only; no learner-level classifier |
| Helpful handling of uncertainty | Prompt asks for a small hint and a simpler follow-up | Implemented instruction; behaviour remains inconsistent |
| Restrict unsupported external knowledge | Prompt grounding instructions | Not reliably achieved; no semantic verifier or calibrated abstention |
| Recognise corrections and distinguish assistance | Prompt instructions; stored student/buddy roles | Partial; model attribution errors observed |
| Reflection linked to student and source evidence | Validated student/source IDs; fixed factual introduction; actual passages now visible | Implemented provenance; semantic interpretation remains fallible |
| Local persistence and privacy | SQLite, local models, ignored runtime data; no paid API | Implemented current text path; fresh offline installation not verified |
| Failure/retry handling and isolation | Atomic turn writes, retry IDs, per-session locks, scoped retrieval | Tested software behaviour |
| Recorded speech with editable transcript | Browser WAV conversion, local Whisper base, explicit review then send, transcript provenance | Implemented; unit/API tests and checkpoint load pass; user reports microphone fix works; formal WER evaluation pending |
| Buddy speech and playback controls | Browser local voices only; replay, stop and optional automatic replies | Implemented controls; audible browser trial pending |
| Optional separate diagram practice | Manual image crop + Granite description + explicit review + description and retrieved notes supplied to Qwen | Implemented; first live caption had errors and took 286.725 s; see diagram_implementation.md |
| Meaningful multimodal workflow | MiniLM retrieval, Qwen conversation, Whisper speech and Granite image description | All four paths implemented; caption reliability and CPU latency remain limitations |
| Streaming/low-delay interaction | Non-streaming generation; loading status only | Not implemented; CPU response delay remains material |
| Evidence-based candidate selection | Two installed candidates compared on ten fixed development cases each; raw outputs/timing saved | Initial controlled generation comparison complete; assistant review provisional; retrieval and held-out evaluation still needed |
| Held-out final evaluation/user evaluation | Development feedback exists | Not yet conducted; not a validated user study |
| Independent reproducible installation | Existing Python environment and dependency junction reused | Incomplete; packaging/fresh-install check required |
| Public repository and narrated demo | No publication or video verified in this audit | Outstanding submission work |

The eight-response session cap and six-message generation history are pragmatic resource limits, not pedagogical requirements. Their effects on conversational continuity and complete reflection context need evaluation. Extraction may flatten mathematical notation; it does not interpret diagram content.

## Decisions retained
Keep the architecture: named session -> notes -> source-grounded conversation -> provisional reflection. Do not reintroduce all-reference checking, automatic topic extraction or a Bloom ladder. No prompt change was made during this audit; conversation-v2 and reflection-v2 remain active so the Sets failure is attributable to the recorded configuration. The source visibility change adds no LLM call and does not claim a semantic repair.

## Next work, in dependency order
1. Completed the first bounded LLM comparison; see local_model_comparison_report.md. Review the provisional ratings, address the shared equivalent-notation reflection failure, and verify retrieval with expected passages rather than treating generation-only results as a complete RAG test.
2. Use those results to choose a configuration and explicit behaviour when the notes lack support. Test with notes-specific conventions and paired context/no-context runs; do not regard citations or similarity scores as correctness scores.
3. Speech integration is implemented and the student reports that the audio fix works. Collect formal transcript/reference and latency evidence; playback audibility remains to verify.
4. Separate diagram practice is implemented with manually cropped images, Granite descriptions and review. The first live caption required correction and took 286.725 seconds; the corrected description reached the real buddy. Recover the historical BLIP chapter/outputs and evaluate caption quality/correction burden. Automatic figure extraction is not implemented.
5. Verify the full flow, freeze model/prompt settings and evaluate separate cases. Complete reproducible setup, repository preparation and the demonstration. Finalise report chapters from the accumulated evidence.

## Verification for this revision
25 backend tests passed, including new source-to-reply association, legacy trace compatibility, refusal to guess with inconsistent legacy history, foreign-ID rejection and persistence tests. Frontend production build and lint passed. These tests do not establish model accuracy or browser usability. The user's running server is not restarted automatically. Restart the backend and refresh the frontend to load the new API field and source disclosures; old Sets-session traces remain available and are supported by the compatibility path.

