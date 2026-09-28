"""Reproduce the fixed synthetic MiniLM passage-ranking check."""
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.services import inference  # noqa: E402

fixture = json.loads((ROOT / 'evaluation/cases/retrieval_fresh_v1_cases.json').read_text(encoding='utf-8'))
results = []
for document in fixture['documents']:
    vectors = inference.embed(document['chunks'])
    index = {'chunks': document['chunks'], 'vectors': vectors}
    for case in document['cases']:
        query = document['topic'] + '\n' + case['previous_buddy'] + '\n' + case['student']
        ranking = inference.retrieve(index, query, count=len(document['chunks']))
        expected = set(case['expected_ids'])
        ranks = [rank for rank, row in enumerate(ranking, 1) if row['id'] in expected]
        target_rank = min(ranks) if ranks else None
        results.append({'case_id': case['id'], 'topic': document['topic'],
                        'expected_ids': case['expected_ids'], 'query': query,
                        'top_three': [{'id': row['id'], 'page': row['page'],
                                       'similarity': round(row['similarity'], 6)} for row in ranking[:3]],
                        'target_rank': target_rank,
                        'hit_at_1': target_rank is not None and target_rank <= 1,
                        'hit_at_3': target_rank is not None and target_rank <= 3})

summary = {'questions': len(results),
           'hit_at_1': sum(item['hit_at_1'] for item in results),
           'hit_at_3': sum(item['hit_at_3'] for item in results),
           'mean_reciprocal_rank': round(sum(1 / item['target_rank'] for item in results
                                             if item['target_rank']) / len(results), 4)}
record = {'fixture_id': fixture['id'], 'fixture_status': fixture['status'],
          'scope': fixture['scope'], 'run_utc': datetime.now(timezone.utc).isoformat(),
          'python': platform.python_version(), 'model': 'sentence-transformers/all-MiniLM-L6-v2',
          'method': 'App inference.embed plus inference.retrieve; full passage ranking per query',
          'summary': summary, 'results': results}
destination = ROOT / 'evaluation/results/retrieval_fresh_v1_results.json'
destination.write_text(json.dumps(record, indent=2), encoding='utf-8')
print(json.dumps(summary, indent=2))
print(destination)
