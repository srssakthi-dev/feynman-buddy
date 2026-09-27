"""Three local-model DEVELOPMENT probes; human review required, no accuracy score.

Uses the original PDF's extracted passages as controlled context, bypassing retrieval
to isolate generation. Does not modify live sessions or restart the application.
Run with backend on PYTHONPATH and --pdf pointing to the development benchmark.
"""
import argparse
import json
from pathlib import Path
from app.services import inference
from app.services.documents import extract_notes

parser = argparse.ArgumentParser()
parser.add_argument('--pdf', type=Path, required=True)
args = parser.parse_args()
sources = extract_notes(args.pdf.read_bytes(), args.pdf.name)['chunks']
student = ('gradient descent is an optimization algorithm that helps machine learning models learn properly. '
           'it has a loss function which measures how badly the model parameters perform. '
           'the lower the value of the loss function the better the model learns.')
question = ("That's a solid start! You mentioned the goal is to find parameters with lower loss. "
            'Since the gradient points uphill, how does moving opposite to it actually help us go downhill?')
bad_hint = ("Think of the gradient as a map showing which way gets steeper up. If you walk exactly opposite "
            "that arrow, you're guaranteed to go down, even if you don't know where the bottom is yet. "
            'Does that help visualize the direction?')
messages = [
    {'id': 'B0', 'role': 'buddy', 'text': 'Hey! What are you going to teach me about Gradient descent today? Start wherever feels natural.'},
    {'id': 'S1', 'role': 'student', 'text': student},
    {'id': 'B1', 'role': 'buddy', 'text': question},
    {'id': 'S2', 'role': 'student', 'text': 'im not very sure'},
    {'id': 'B2', 'role': 'buddy', 'text': bad_hint},
]
record = {'kind': 'targeted-development-generation-probes', 'model': inference.MODEL,
          'conversation_prompt': inference.PROMPT_VERSION, 'reflection_prompt': inference.REFLECTION_VERSION,
          'sources': sources, 'original_transcript': messages, 'results': [],
          'limitations': 'One run per probe, known development case, all three passages supplied. Not held-out accuracy or an end-to-end retrieval test.'}
output = Path(__file__).parent / 'results' / 'grounding_regression_v2.json'
output.parent.mkdir(exist_ok=True)


def save():
    output.write_text(json.dumps(record, indent=2), encoding='utf-8')


save()
probes = [
    ('opening_followup', lambda: inference.reply('Gradient descent', messages[:1], student, sources, inference.MODEL)),
    ('uncertainty_hint', lambda: inference.reply('Gradient descent', messages[:3], 'im not very sure', sources, inference.MODEL)),
    ('reflection_with_false_buddy_hint', lambda: inference.reflect('Gradient descent', messages, sources, inference.MODEL)),
]
for name, run in probes:
    print('RUNNING', name, flush=True)
    try:
        value, trace = run()
        record['results'].append({'probe': name, 'output': value, 'trace': trace})
        print(name, json.dumps(value), trace['wall_seconds'], flush=True)
    except Exception as exc:
        record['results'].append({'probe': name, 'error': str(exc)})
        print(name, 'ERROR', str(exc), flush=True)
    save()
