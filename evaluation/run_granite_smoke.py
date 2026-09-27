"""One reproducible development example, not a caption accuracy benchmark."""
import argparse
import json
import sys
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.services import vision

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'evaluation/results/granite_smoke_v1.json')
    args = parser.parse_args()
    picture, metadata = vision.prepare_image(args.image.read_bytes())
    description, trace = vision.describe(picture)
    with urlopen('http://127.0.0.1:11434/api/tags') as response:
        models = json.load(response)['models']
    result = {'scope': 'Single development image; not a held-out accuracy estimate.',
        'input_file': args.image.name, 'description': description, 'trace': {**trace, **metadata},
        'installed_model': next(item for item in models if item['name'] == vision.MODEL),
        'review': 'Pending visual inspection; no human rating yet.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
