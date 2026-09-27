"""Run the historical BLIP configuration on Granite's exact prepared image.

Development case study, not a held-out benchmark. No model downloads or app changes.
"""
import argparse
import hashlib
import io
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.services.vision import prepare_image


def run(image_path, granite_path, output):
    started = time.perf_counter()
    import torch
    import transformers
    from transformers import BlipProcessor, BlipForConditionalGeneration
    from transformers.utils.hub import cached_file
    from PIL import Image
    import_seconds = time.perf_counter() - started
    granite = json.loads(granite_path.read_text(encoding='utf-8'))
    picture, metadata = prepare_image(image_path.read_bytes())
    if metadata['image_sha256'] != granite['trace']['image_sha256']:
        raise ValueError('Prepared image differs from the saved Granite input; comparison stopped.')
    model_id = 'Salesforce/blip-image-captioning-base'
    result = {'scope': 'One matched development image; one run per configuration; not held-out accuracy.',
        'created_at_utc': datetime.now(timezone.utc).isoformat(), 'model': model_id,
        'input_file': image_path.name, 'image': metadata,
        'granite_evidence': granite_path.name, 'matched_prepared_image': True,
        'settings': {'prompt': None, 'max_new_tokens': 40, 'seed': 42,
                     'device': 'cpu', 'local_files_only': True},
        'environment': {'python': platform.python_version(), 'torch': torch.__version__,
                        'transformers': transformers.__version__, 'torch_threads': torch.get_num_threads()},
        'timings': {'imports_seconds': round(import_seconds, 3)},
        'review_criteria': ['axes/variables', 'A and B as points on one curve',
            'gradient arrow points right', 'update arrow points left', 'B has lower loss than A',
            'unsupported claims', 'correction needed before use'],
        'reviewer_note': 'Criteria recorded for this development case after seeing Granite; not blinded or independent.'}
    inference_start = time.perf_counter()
    try:
        torch.manual_seed(42)
        processor = BlipProcessor.from_pretrained(model_id, local_files_only=True)
        model = BlipForConditionalGeneration.from_pretrained(model_id, local_files_only=True).to('cpu')
        model.eval()
        loaded = time.perf_counter()
        config_path = Path(cached_file(model_id, 'config.json', local_files_only=True))
        result['cached_revision'] = config_path.parent.name
        result['generation_defaults'] = model.generation_config.to_dict()
        result['processor_config'] = processor.image_processor.to_dict()
        inputs = processor(Image.open(io.BytesIO(picture)).convert('RGB'), return_tensors='pt')
        prepared = time.perf_counter()
        with torch.inference_mode():
            tokens = model.generate(**inputs, max_new_tokens=40)
        result['description'] = processor.decode(tokens[0], skip_special_tokens=True)
        result['output_token_ids'] = tokens[0].tolist()
        completed = time.perf_counter()
        result['timings'].update({'load_seconds': round(loaded-inference_start, 3),
            'preprocess_seconds': round(prepared-loaded, 3),
            'generate_and_decode_seconds': round(completed-prepared, 3),
            'load_through_caption_seconds': round(completed-inference_start, 3)})
        result['status'] = 'completed'
    except Exception as exc:
        result['status'] = 'failed'
        result['error'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        result['runner_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'description': result['description'], 'timings': result['timings'],
                      'matched_prepared_image': True, 'output': str(output)}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image', type=Path)
    parser.add_argument('--granite', type=Path, default=ROOT/'evaluation/results/granite_smoke_v1.json')
    parser.add_argument('--output', type=Path, default=ROOT/'evaluation/results/blip_matched_diagram_v1.json')
    args = parser.parse_args()
    run(args.image, args.granite, args.output)
