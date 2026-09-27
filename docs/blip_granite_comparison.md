# BLIP and Granite: matched diagram development comparison

28 September 2026. This is a single-image development case study, not a held-out benchmark or an estimate of general model accuracy. The comparison uses measured local outputs. Review was performed by the coding assistant and is provisional, not an independent human rating.

## Purpose and method

Assess whether the historical BLIP captioning configuration and the newly integrated Granite configuration produce enough visual information to support a diagram explanation conversation. Both received the same prepared gradient-descent image, verified by SHA-256: `5d04a939e0540c972488a1ba2d541323fbb7f559f09464de9f42ceb7f9905a44`. Its dimensions before model-specific processing were 1280 × 658. Neither captioning call received the surrounding notes or the student's explanation.

The figure plots loss L(w) against parameter w, with points A and B on one curve. B is below and left of A. The gradient-direction arrow points right; the update-direction arrow points left. No numerical coordinates are supplied. These visible facts provide the reference for the qualitative review.

Granite's existing recorded run was reused unchanged. BLIP was executed subsequently on the matched image using cached local weights, CPU inference and the old implementation's unconditional captioning configuration (`max_new_tokens=40`). No model downloads were required and the active application's model selection was not changed. The input, settings, cached model revision, processor configuration, raw token IDs, library versions and timings are saved with the result.

## Measured outputs

BLIP (`Salesforce/blip-image-captioning-base`):

> a graph with a line going up and down

Granite (`granite3.2-vision:2b`):

> The diagram shows a one-dimensional illustration of a loss function L(w) plotted against two parameters, A and B. The loss function is a function of the parameters, and the gradient direction is indicated by an arrow. The diagram also includes a parameter w, which is a variable in the loss function. The positions of the points A and B are schematic and do not have specific numerical values. The diagram is a schematic illustration and does not provide specific numerical values for the parameters.

| Review criterion | BLIP | Granite |
|---|---|---|
| Recognises a graph/curve | Yes, generic description | Yes, recognises a loss function |
| Names axes/variables meaningfully | Omits them | Names L(w) and w, but misdescribes the plot as against A and B |
| Identifies A and B as points on one curve | Omits them | Mentions points later, but first incorrectly calls them two parameters |
| Describes rightward gradient arrow | Omitted | Mentions a gradient arrow but omits direction |
| Describes leftward update arrow | Omitted | Omitted |
| Compares loss at B with A | Omitted | Omitted |
| Unsupported content | No specific label/value invention; description too generic | Incorrect interpretation of A and B |
| Adequate without correction for this practice | No | No |

The Granite caption is more detailed, but greater detail is not equivalent to greater reliability. Both omit the key opposing directions that the intended exercise asks the student to explain. Granite also introduces a misleading interpretation. BLIP's limitations are mainly omissions in this example. No numerical accuracy score is assigned.

## Timing and comparability

| Measurement | BLIP | Granite |
|---|---:|---:|
| Local model loading | 0.785 s | 5.583 s |
| Image preprocessing outside model | 0.034 s | Included in server processing |
| Generation and decoding / server evaluation | 3.301 s | 38.416 s |
| Server prompt/image evaluation | Included in BLIP generation call | 242.571 s |
| Model loading through returned caption | **4.120 s** | **286.725 s** |

BLIP also required 11.377 seconds for Python imports in the fresh evaluation process, separately recorded. That import time is excluded from its 4.120-second figure; Granite used an already running Ollama service. Neither total is a complete fresh-machine startup time. Model-specific timing stages are not equivalent operations.

These are single observations on the same laptop, not averaged latency benchmarks. Runs occurred at different times and background workload was not controlled. BLIP used its own 384 × 384 image processor; Granite used its own vision encoding. BLIP had no text prompt and a 40-token output ceiling; Granite had a detailed instruction and a 300-token ceiling. Neither output approached its configured ceiling in these runs. The experiment compares implemented configurations, not architecture alone, and does not establish a generally applicable speed ratio.

## Implications for the application

Retain the user's selected Granite integration provisionally, but do not justify it as a demonstrated accuracy improvement over BLIP. Its intended document-understanding role is a selection rationale; the measured result exposes remaining limitations. The review step is necessary in this example: the coding assistant corrected the caption before the separate conversation test. That correction is human/assistant intervention, not model success. The conversation and reflection results cannot be used to claim that the raw Granite caption was sufficient.

The approximately five-minute preparation delay is material even though vision runs once per diagram. Ordinary text turns have their own separate latency. This result supports documenting an implemented optional diagram feature with substantial usability and reliability limitations, rather than claiming real-time visual tutoring.

## Relationship to the earlier BLIP experiment

The student separately reported 40 images extracted from one chapter PDF with basic BLIP captions. Those original 40 image/output pairs have not been recovered. This new matched-image result is directly verifiable and independent of that recollection. It happens to reproduce the wording of one previously saved BLIP output, but it does not establish the identity or outcomes of the other historical images.

## Report placement

Chapter 4: explain the separate vision-description, review and conversation stages, and why the original caption and corrected description are stored separately.

Chapter 5: include the comparison table, both actual captions, the test image, timing definitions and limitations. Describe the experiment as a matched development example. A defensible conclusion is that both configurations required correction for the selected directional diagram, while Granite's local processing imposed a substantially longer preparation delay in the observed runs. Do not write that Granite achieved better accuracy or that this constitutes a 40-image benchmark.

## Reproduction and evidence

- `evaluation/run_blip_diagram_comparison.py`: offline BLIP runner with a matched-image hash guard.
- `evaluation/fixtures/gradient_diagram.png`: original development image.
- `evaluation/results/blip_matched_diagram_v1.json`: new BLIP raw result and full configuration.
- `evaluation/results/granite_smoke_v1.json`: preserved Granite result and model identity.
- `evaluation/results/diagram_workflow_smoke_v1.json`: separately labelled corrected-caption conversation test.

Run the BLIP script with the configured Python interpreter and `evaluation/fixtures/gradient_diagram.png` as its image argument. The runner requires the existing cached BLIP weights; it will not download them. Back up or choose a different `--output` path when recording another trial. Further evaluation should use several unseen diagrams with different visual relationships and ratings from the student or another human reviewer, preserving all raw outputs and correction effort.
