"""Local development walkthrough with real PDF, BLIP, retrieval and Qwen."""
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.main import create_app


def main():
    evidence = {'scope': 'Synthetic developer walkthrough, not a user study or held-out evaluation.',
                'created_at_utc': datetime.now(timezone.utc).isoformat(), 'steps': []}
    output = ROOT/'evaluation/results/topic_figure_smoke_v1.json'
    try:
        with tempfile.TemporaryDirectory() as directory, TestClient(create_app(Path(directory)/'test.sqlite3')) as client:
            def step(label, request):
                started = time.perf_counter()
                response = request()
                elapsed = round(time.perf_counter()-started, 3)
                evidence['steps'].append({'name': label, 'status': response.status_code,
                                          'wall_seconds': elapsed})
                if response.status_code >= 400:
                    raise RuntimeError(f'{label}: HTTP {response.status_code} {response.text[:500]}')
                return response

            sid = step('create-session', lambda: client.post('/api/sessions', json={
                'name':'Gradient descent'})).json()['id']
            base = '/api/sessions/' + sid
            pdf = (ROOT/'evaluation/fixtures/gradient_descent_benchmark_notes.pdf').read_bytes()
            image = (ROOT/'evaluation/fixtures/gradient_diagram.png').read_bytes()
            step('ingest-notes', lambda: client.post(base+'/documents', files={
                'file':('gradient_descent_benchmark_notes.pdf', pdf, 'application/pdf')}))
            data = step('caption-figure-with-BLIP', lambda: client.post(base+'/figures', data={
                'page':2, 'printed_caption':'A single update on an illustrative loss curve',
                'request_id':'figure-1'}, files={'file':('gradient_diagram.png', image, 'image/png')})).json()
            figure = data['figures'][0]
            evidence['raw_blip_caption'] = figure['original_caption']
            fid = figure['id']
            # Correction supplied by the coding assistant after inspecting this known figure.
            corrected = ('The graph plots loss L(w) against parameter w. A and B are points on one curve; '
                         'B is below and left of A. The gradient arrow points right, and the update arrow points left. '
                         'The positions are schematic, with no numerical values.')
            step('review-figure', lambda: client.post(base+f'/figures/{fid}/review', json={'text':corrected}))
            step('start-topic', lambda: client.post(base+'/start'))
            ordinary = step('ordinary-topic-turn', lambda: client.post(base+'/turn', json={
                'text':'Gradient descent adjusts parameters to try to reduce a loss function.',
                'request_id':'turn-1'})).json()
            evidence['ordinary_reply'] = ordinary['messages'][-1]['text']
            evidence['ordinary_sources'] = ordinary['reply_sources'][ordinary['messages'][-1]['id']]
            selected = step('select-figure-in-same-session', lambda: client.post(base+f'/figures/{fid}/discuss')).json()
            assert selected['session']['id'] == sid and selected['active_figure_id'] == fid
            figure_turn = step('explain-figure-turn', lambda: client.post(base+'/turn', json={
                'text':'The gradient arrow points right, whereas the update points left. B is lower on the loss curve than A.',
                'request_id':'turn-2'})).json()
            evidence['figure_reply'] = figure_turn['messages'][-1]['text']
            evidence['figure_sources'] = figure_turn['reply_sources'][figure_turn['messages'][-1]['id']]
            assert evidence['figure_sources'][0]['id'] == 'FIGURE-' + fid
            returned = step('return-to-topic', lambda: client.post(base+'/figures/return-to-topic')).json()
            assert returned['active_figure_id'] is None and returned['session']['id'] == sid
            finished = step('reflect-on-one-conversation', lambda: client.post(base+'/finish')).json()
            evidence['reflection'] = finished['reflection']
            evidence['messages'] = finished['messages']
            evidence['traces'] = client.get(base+'/export').json()['traces']
            evidence['same_session_id'] = sid
            evidence['status'] = 'completed'
    except Exception as exc:
        evidence['status'] = 'failed'
        evidence['error'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(evidence, indent=2), encoding='utf-8')
        print(json.dumps({'status':evidence['status'], 'steps':evidence['steps'],
                          'ordinary_reply':evidence.get('ordinary_reply'),
                          'figure_reply':evidence.get('figure_reply'),
                          'output':str(output)}, indent=2), flush=True)


if __name__ == '__main__':
    main()
