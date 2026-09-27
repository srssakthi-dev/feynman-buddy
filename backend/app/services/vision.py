"""One local image description per diagram practice; no vision call per turn."""
import base64
import hashlib
import io
import json
import time
import warnings
from urllib.request import Request, urlopen
from PIL import Image, ImageOps
from app.services.inference import LOCK, PROMPTS

MODEL = 'granite3.2-vision:2b'
PROMPT_VERSION = 'diagram-caption-v1'
MAX_IMAGE_BYTES = 8 * 1024 * 1024


def prepare_image(data):
    """Validate actual image bytes, remove metadata, and bound inference size."""
    if not data or len(data) > MAX_IMAGE_BYTES:
        raise ValueError('Choose a PNG or JPEG smaller than 8 MB.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as original:
                if original.format not in ('PNG', 'JPEG'):
                    raise ValueError('Choose a PNG or JPEG image.')
                if original.width * original.height > 16_000_000 or min(original.size) < 32:
                    raise ValueError('Use a clear diagram crop between 32 pixels and 16 megapixels.')
                original.load()
                picture = ImageOps.exif_transpose(original).convert('RGBA')
                background = Image.new('RGBA', picture.size, 'white')
                background.alpha_composite(picture)
                picture = background.convert('RGB')
                picture.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
                output = io.BytesIO()
                picture.save(output, format='PNG')
                return output.getvalue(), {'width': picture.width, 'height': picture.height,
                    'original_sha256': hashlib.sha256(data).hexdigest(),
                    'image_sha256': hashlib.sha256(output.getvalue()).hexdigest()}
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError('This image could not be read. Save the diagram as a PNG or JPEG and retry.') from exc


def describe(image):
    prompt = (PROMPTS / f'{PROMPT_VERSION}.txt').read_text(encoding='utf-8')
    payload = {'model': MODEL, 'stream': False, 'keep_alive': 0,
        'messages': [{'role': 'user', 'content': prompt,
                      'images': [base64.b64encode(image).decode('ascii')]}],
        'options': {'temperature': 0, 'seed': 42, 'num_ctx': 16384, 'num_predict': 300}}
    started = time.perf_counter()
    # Release Granite after captioning to leave RAM for the conversation model.
    with LOCK:
        with urlopen(Request('http://127.0.0.1:11434/api/chat',
                data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'}),
                timeout=600) as response:
            result = json.load(response)
    description = result.get('message', {}).get('content', '').strip()
    if not description:
        raise ValueError('Granite returned no description. Try a clearer diagram crop.')
    return description, {'model': MODEL, 'prompt_version': PROMPT_VERSION, 'prompt': prompt,
        'options': payload['options'], 'keep_alive': 0,
        'wall_seconds': round(time.perf_counter() - started, 3),
        **{key: result.get(key) for key in ('load_duration', 'prompt_eval_duration',
            'eval_duration', 'prompt_eval_count', 'eval_count', 'done_reason')}}


def diagram_source(diagram):
    return {'id': 'DIAGRAM', 'page': diagram['page'], 'kind': 'reviewed_diagram_description',
        'text': diagram['approved_caption'], 'similarity': None,
        'selection': 'Required diagram context; not similarity-ranked.',
        'provenance': 'AI description reviewed by the student; may still contain errors.'}
