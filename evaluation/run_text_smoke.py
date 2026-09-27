"""Actual local-model integration check, separate from mocked workflow tests.

Usage: python evaluation/run_text_smoke.py --pdf PATH --api http://127.0.0.1:8101
The input is a project-authored development fixture, not held-out evaluation.
"""
import argparse
import json
import time
import uuid
from pathlib import Path
import httpx

parser = argparse.ArgumentParser()
parser.add_argument('--pdf', type=Path, required=True)
parser.add_argument('--api', default='http://127.0.0.1:8101')
args = parser.parse_args()
output = Path(__file__).parent / 'results'
output.mkdir(exist_ok=True)
record = {'kind': 'development-integration', 'steps': []}
with httpx.Client(timeout=240) as client:
    response = client.post(args.api + '/api/sessions', json={'name': 'Gradient descent'})
    response.raise_for_status()
    sid = response.json()['id']
    base = args.api + '/api/sessions/' + sid
    record['session_id'] = sid
    print('SESSION', sid, flush=True)
    with args.pdf.open('rb') as pdf:
        response = client.post(base + '/documents', files={'file': (args.pdf.name, pdf, 'application/pdf')})
    response.raise_for_status()
    document = response.json()['document']
    print('UPLOADED', document['page_count'], 'pages,', len(document['chunks']), 'passages', flush=True)
    response = client.post(base + '/start')
    response.raise_for_status()
    print('OPENING', response.json()['messages'][-1]['text'], flush=True)
    for text in [
        'Gradient descent changes the parameters of a model to reduce its loss.',
        'We move in the same direction as the gradient because the gradient points downhill.',
        'I need to correct that: the gradient points towards increasing loss, so we update in the opposite direction. If the gradient is positive, subtracting it decreases the parameter.',
    ]:
        started = time.perf_counter()
        response = client.post(base + '/turn', json={'text': text, 'request_id': str(uuid.uuid4())})
        response.raise_for_status()
        answer = response.json()['messages'][-1]['text']
        seconds = round(time.perf_counter() - started, 2)
        record['steps'].append({'student': text, 'buddy': answer, 'seconds': seconds})
        print('TURN', seconds, answer, flush=True)
        (output / 'text_smoke_progress.json').write_text(json.dumps(record, indent=2))
    started = time.perf_counter()
    response = client.post(base + '/finish')
    response.raise_for_status()
    record['reflection_seconds'] = round(time.perf_counter() - started, 2)
    response = client.get(base + '/export')
    response.raise_for_status()
    record['export'] = response.json()
    (output / 'text_smoke.json').write_text(json.dumps(record, indent=2))
    print('REFLECTION', record['reflection_seconds'], json.dumps(record['export']['reflection']), flush=True)
