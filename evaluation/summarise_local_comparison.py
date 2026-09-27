"""Summarise measurements without automatically judging educational quality."""
import json
import statistics
from pathlib import Path

folder = Path(__file__).parent / 'results/local_comparison_v1'
record = json.loads((folder / 'raw_results.json').read_text(encoding='utf-8'))
if not record.get('finished_utc'):
    raise SystemExit('Comparison is still running; do not publish a partial summary as complete.')
summary = {}
transcript = ['# Local model comparison: complete outputs',
              'Synthetic development fixtures. No outputs omitted. See protocol and review for limitations.']
for model in record['models_in_order']:
    summary[model] = {}
    for kind in ['reply', 'reflect']:
        rows = [r for r in record['results'] if r['model'] == model and r['kind'] == kind]
        elapsed = [r['elapsed_seconds'] for r in rows]
        summary[model][kind] = dict(attempts=len(rows), completed=sum(r['status'] == 'completed' for r in rows),
            mean_seconds=round(statistics.mean(elapsed), 3), median_seconds=round(statistics.median(elapsed), 3),
            min_seconds=min(elapsed), max_seconds=max(elapsed))
for row in record['results']:
    transcript += [f"## {row['model']} / {row['case_id']}",
                   f"Criterion: {row['acceptance']}",
                   f"Status: {row['status']}. Elapsed: {row['elapsed_seconds']} seconds.",
                   'Raw output:', '```text\n' + row['capture'].get('raw_output', row.get('error', 'No output')) + '\n```']
    if row['kind'] == 'reflect' and row.get('output'):
        cleaned = {key: [{'observation': i['observation'], 'student_ids': [e['id'] for e in i['evidence']],
                          'source_ids': [s['id'] for s in i['sources']]} for i in row['output'][key]]
                   for key in ['explained', 'revisit']}
        transcript += ['After application evidence validation:', '```json\n' + json.dumps(cleaned, indent=2) + '\n```']
(folder / 'timing_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
(folder / 'complete_outputs.md').write_text('\n\n'.join(transcript), encoding='utf-8')
print(json.dumps(summary, indent=2))
