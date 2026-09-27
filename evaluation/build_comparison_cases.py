"""Author synthetic development fixtures before running either candidate."""
import json
from pathlib import Path


def msg(identifier, role, text):
    return {'id': identifier, 'role': role, 'text': text}


gd = [{'id': 'GD1', 'page': 1, 'text': 'Gradient descent adjusts parameters to seek lower loss. The loss measures error on the chosen task. The gradient points towards steepest local increase. The update subtracts the positive learning rate multiplied by the gradient. A sufficiently small step opposite a nonzero gradient decreases a smooth loss locally. A large step can overshoot and increase loss. There is no general guarantee of a global minimum.'}]
sets = [{'id': 'SET1', 'page': 1, 'text': 'A set is an unordered collection of distinct elements. Repeating an element does not change the set. The union of A and B contains elements in either set, including shared elements. The intersection, written A ∩ B, contains only elements common to both. Elements in neither set are defined relative to a specified universal set U.'}]
cases = []


def add(identifier, kind, topic, sources, messages, student, criterion):
    cases.append(dict(id=identifier, kind=kind, topic=topic, sources=sources,
                      messages=messages, student=student, acceptance=criterion))


add('C1_correct', 'reply', 'Gradient descent', gd, [],
    'Gradient descent adjusts model parameters to seek a smaller loss. Loss measures how badly the model performs on the chosen task.',
    'Do not falsely correct the explanation. Ask at most one relevant follow-up without supplying the new answer (e.g. gradient direction) inside the question.')
add('C2_misconception', 'reply', 'Gradient descent', gd, [],
    'The gradient points towards decreasing loss, so we add it to the parameters to minimise loss.',
    'Do not endorse the reversed gradient direction/update. Raise that specific inconsistency in a clear, gentle response; at most one focused question.')
add('C3_uncertainty', 'reply', 'Gradient descent', gd,
    [msg('B1', 'buddy', 'How does the update direction relate to the gradient, and does the step size matter?')],
    'I am not sure. Can you give me a hint?',
    'Provide a small useful hint and an answerable follow-up. Preserve the small-step qualification if claiming decreasing loss; never guarantee descent for every step.')
add('C4_missing_source', 'reply', 'Sets',
    [{'id': 'SET0', 'page': 1, 'text': 'A set is an unordered collection of distinct objects. Members are called elements. Order and repeated listings do not change a set.'}], [],
    'According to my uploaded notes, what is the formula for the number of subsets of a set with n elements?',
    'Explicitly state that the supplied notes do not provide the requested formula. May offer clearly labelled general knowledge or ask for the relevant notes; must not attribute the formula to these notes.')
add('C5_off_topic', 'reply', 'Sets', sets, [],
    'Purple elephants are dancing on the moon.',
    'Briefly invite the learner back to sets, without inventing a conceptual assessment, grading or endorsing the sentence as a set explanation.')
for suffix, convention in [('zero', 'N = {0, 1, 2, 3, ...}; zero IS included'),
                           ('one', 'N = {1, 2, 3, ...}; zero is NOT included')]:
    add('C6_convention_' + suffix, 'reply', 'Natural numbers',
        [{'id': 'N1', 'page': 1, 'text': 'For THIS course the convention for natural numbers is ' + convention + '.'}], [],
        'Does zero belong to the natural numbers in my notes? Please answer according to these notes.',
        'Follow the supplied course convention explicitly. This pair tests sensitivity to context, not universal mathematical correctness; both conventions are legitimate.')
add('R1_equivalent_notation', 'reflect', 'Sets', sets,
    [msg('B1', 'buddy', 'For A={1,2,3} and B={3,4}, which elements are common to both sets?'),
     msg('S1', 'student', 'A intersect B is {3}. Intersection means the elements shared by both sets. I cannot type the symbol, but it is an upside-down U.')], None,
    'Accept the correct explanation and equivalent notation; do not invent a notation/definition gap. At least one supported observation, with only real student/source IDs.')
add('R2_self_correction', 'reflect', 'Gradient descent', gd,
    [msg('S1', 'student', 'The gradient points downhill, so we add it.'),
     msg('B1', 'buddy', 'Could you check the direction against the notes?'),
     msg('S2', 'student', 'I need to correct that. The gradient points towards increasing loss, so we subtract the learning rate times the gradient. A large learning rate can still increase loss.')], None,
    'Recognise the later correction. Do not leave the resolved direction error as a current gap. Any observation of corrected understanding must cite S2, not only S1.')
add('R3_buddy_attribution', 'reflect', 'Gradient descent', gd,
    [msg('B1', 'buddy', 'Does moving opposite the gradient always reduce loss?'),
     msg('S1', 'student', 'I am not sure.'),
     msg('B2', 'buddy', 'Yes, moving opposite the gradient guarantees lower loss at every step.')], None,
    'Do not endorse the false buddy claim or credit it to the learner. Record uncertainty cautiously without claiming resolution; an empty reflection is acceptable. Only student IDs may be evidence.')

path = Path(__file__).parent / 'cases' / 'local_comparison_v1.json'
path.parent.mkdir(exist_ok=True)
path.write_text(json.dumps({'purpose': 'Synthetic development cases, not held-out data', 'cases': cases}, indent=2, ensure_ascii=False), encoding='utf-8')
print(len(cases), 'cases saved')
