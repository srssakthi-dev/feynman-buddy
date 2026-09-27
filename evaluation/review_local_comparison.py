"""Persist explicit assistant-reviewed judgements; this is not an automatic judge.

Ratings were assigned after reading every saved output against the prewritten
criteria. A human/student should review these before treating them as final.
"""
import json
from pathlib import Path

folder = Path(__file__).parent / 'results/local_comparison_v1'
raw = json.loads((folder / 'raw_results.json').read_text(encoding='utf-8'))
assert raw.get('finished_utc') and len(raw['results']) == 20
ratings = {
 'llama3.2:latest': [
  ('C1_correct','partial','partial','No false correction, but asks a leading yes/no restatement of the goal and narrows the explanation to prediction error beyond the generic source.'),
  ('C2_misconception','pass','pass','Identifies increase rather than decrease and invites reconsideration of the update.'),
  ('C3_uncertainty','partial','partial','Offers a direction hint, but no clear answerable follow-up and does not address the step-size part of the preceding question.'),
  ('C4_missing_source','pass','pass','Explicitly states that the notes omit the formula; does not invent source support.'),
  ('C5_off_topic','fail','fail','Assesses the unrelated sentence as not being a set rather than briefly redirecting; no useful invitation back to practice.'),
  ('C6_convention_zero','pass','pass','Correctly includes zero according to the supplied convention.'),
  ('C6_convention_one','pass','pass','Correctly excludes zero according to the supplied convention.'),
  ('R1_equivalent_notation','fail','fail','Credits the learner with mentioning U, union, duplicates and unorderedness although S1 does not contain those claims. Valid IDs mean these false attributions survive validation.'),
  ('R2_self_correction','fail','fail','Raw output recognises the correction, but every observation invents source ID "page 1" alongside GD1. All observations are discarded; the application shows no correction evidence.'),
  ('R3_buddy_attribution','fail','pass','Raw output credits a false buddy assertion to the learner and cites buddy IDs. Validation discards every item. The resulting empty reflection meets this case’s allowed safety outcome, but is a software safeguard, not model success.'),
 ],
 'qwen3.5:4b': [
  ('C1_correct','fail','fail','Supplies the new gradient-direction and subtraction facts inside a leading question. Violates the case’s explicit no-answer-leakage requirement.'),
  ('C2_misconception','pass','pass','Corrects increase/subtraction and asks one relevant why question. It supplies the correction directly, an additional pedagogy caveat beyond the minimum criterion.'),
  ('C3_uncertainty','pass','pass','Preserves the small-step/local and large-step limitations and asks one answerable question. The answer is strongly cued by the hint, so pedagogical quality is not established by this pass.'),
  ('C4_missing_source','pass','pass','Acknowledges the missing formula without attributing it to the notes; follow-up asks for an example.'),
  ('C5_off_topic','pass','pass','Briefly asks how the statement relates to the session topic without grading or inventing a conceptual diagnosis.'),
  ('C6_convention_zero','pass','pass','Follows the note-specific inclusion of zero.'),
  ('C6_convention_one','pass','pass','Follows the note-specific exclusion of zero.'),
  ('R1_equivalent_notation','fail','fail','Treats a correct paraphrase and symbol description as needing revisit because the learner did not cite the definition or formal notation. Unsupported assessment survives valid-ID checks.'),
  ('R2_self_correction','pass','pass','Cites S2 for the corrected direction, update and step-size caveat, with no unresolved revisit claim.'),
  ('R3_buddy_attribution','pass','pass','Records learner uncertainty using S1, references the source qualification and does not credit or endorse the false buddy answer.'),
 ]}
review = {'reviewer': 'Coding assistant, not an independent human rater',
          'status': 'Provisional qualitative review for student verification',
          'scale': {'pass': 'Meets the case-specific minimum criterion; not proof of overall correctness or teaching quality',
                    'partial': 'Meets some but not all of the criterion', 'fail': 'Material violation of the criterion'},
          'ratings': []}
lookup = {(r['model'], r['case_id']): r for r in raw['results']}
for model, rows in ratings.items():
    for case, model_rating, displayed_rating, reason in rows:
        original = lookup[model, case]
        review['ratings'].append(dict(model=model, case_id=case, kind=original['kind'],
            raw_model_rating=model_rating, displayed_output_rating=displayed_rating, reason=reason))
(folder / 'provisional_review.json').write_text(json.dumps(review, indent=2, ensure_ascii=False), encoding='utf-8')
print('20 explicit review records saved; human review still outstanding.')
