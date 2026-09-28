"""Recheck a documented false attribution with a versioned prompt; development only."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'backend'))
from app.services import inference

case = json.loads((ROOT/'evaluation/results/topic_figure_smoke_v1.json').read_text(encoding='utf-8'))
sources = {}
for trace in case['traces']:
    for source in trace.get('sources', []):
        sources[source['id']] = source
ordered = [item for item in sources.values() if item.get('kind') == 'reviewed_figure_description']
ordered += [item for item in sources.values() if item.get('kind') != 'reviewed_figure_description']
result = {'scope':'Development regression on the same synthetic conversation; not independent evaluation.',
          'original_case':'topic_figure_smoke_v1.json',
          'earlier_reflection':case['reflection'], 'sources':ordered}
output = ROOT/'evaluation/results/topic_figure_reflection_v2_recheck.json'
try:
    reflection, trace = inference.reflect('Gradient descent', case['messages'], ordered,
                                          'qwen3.5:4b')
    result.update({'status':'completed','reflection':reflection,'trace':trace})
except Exception as exc:
    result.update({'status':'failed','error':f'{type(exc).__name__}: {exc}'})
    raise
finally:
    output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'status':result['status'], 'output':str(output),
                      'observations':[item['observation'] for item in
                          (result.get('reflection') or {}).get('explained',[])]}, indent=2))
