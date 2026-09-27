"""Use the real inference functions, recording raw calls before reflection parsing.

No live session mutation. Fixed contexts isolate generation from retrieval.
One run per candidate/case, sequential candidate blocks; no automatic judge.
"""
import hashlib
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from app.services import inference

root = Path(__file__).resolve().parents[1]
case_path = root / 'evaluation/cases/local_comparison_v1.json'
cases = json.loads(case_path.read_text(encoding='utf-8'))['cases']
out = root / 'evaluation/results/local_comparison_v1'
out.mkdir(parents=True, exist_ok=True)
result_path = out / 'raw_results.json'
if result_path.exists():
    raise SystemExit('Preserving existing results. Use a new version/directory for a rerun.')
models = ['llama3.2:latest', 'qwen3.5:4b']
with urlopen('http://127.0.0.1:11434/api/tags') as response:
    tags = json.load(response)
with urlopen('http://127.0.0.1:11434/api/version') as response:
    version = json.load(response)
prompts = {name: (inference.PROMPTS / (name + '.txt')).read_text(encoding='utf-8')
           for name in [inference.PROMPT_VERSION, inference.REFLECTION_VERSION]}
record = {'started_utc': datetime.now(timezone.utc).isoformat(), 'purpose': 'development candidate comparison',
          'models_in_order': models, 'installed_model_metadata': tags, 'ollama_version': version,
          'platform': platform.platform(), 'prompts': prompts,
          'case_sha256': hashlib.sha256(case_path.read_bytes()).hexdigest(),
          'inference_sha256': hashlib.sha256(Path(inference.__file__).read_bytes()).hexdigest(),
          'settings': {'temperature': 0.2, 'seed': 42, 'stream': False, 'qwen_think': False,
                       'reply_context': 4096, 'reflection_context': 8192,
                       'reply_max_tokens': 160, 'reflection_max_tokens': 1000, 'timeout_seconds': 180},
          'limitations': ['One run per case/model; not statistically powered.',
                         'Fixed supplied passages; does not evaluate retrieval.',
                         'Sequential model blocks; cache and warm-up affect latency.',
                         'No human participant or learning-gain evaluation.',
                         'Current prompt was previously refined using Qwen; not model-neutral prompt optimisation.'],
          'results': []}
original_generate = inference.generate
capture = {}


def traced_generate(messages, model, max_tokens=160, structured=False):
    capture.update(request_messages=messages, max_tokens=max_tokens, structured=structured)
    raw, trace = original_generate(messages, model, max_tokens, structured)
    capture.update(raw_output=raw, generation_trace=trace)
    return raw, trace


inference.generate = traced_generate


def save():
    temporary = out / 'raw_results.tmp'
    temporary.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding='utf-8')
    temporary.replace(result_path)


save()
for model in models:
    for case in cases:
        capture = {}
        started = time.perf_counter()
        print('RUN', model, case['id'], flush=True)
        result = {'model': model, 'case_id': case['id'], 'kind': case['kind'], 'acceptance': case['acceptance']}
        try:
            if case['kind'] == 'reply':
                output, trace = inference.reply(case['topic'], case['messages'], case['student'], case['sources'], model)
            else:
                output, trace = inference.reflect(case['topic'], case['messages'], case['sources'], model)
            result.update(output=output, trace=trace, status='completed')
        except Exception as exc:
            result.update(status='error', error_type=type(exc).__name__, error=str(exc))
        result.update(capture=capture, elapsed_seconds=round(time.perf_counter() - started, 3))
        record['results'].append(result)
        save()
        print('DONE', model, case['id'], result['status'], result['elapsed_seconds'], flush=True)
record['finished_utc'] = datetime.now(timezone.utc).isoformat()
save()
