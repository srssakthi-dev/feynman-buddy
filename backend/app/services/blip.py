"""Fast, local baseline captioning for optional figures in topic practice."""
import io
import time
from PIL import Image
from app.services.inference import LOCK

MODEL = 'Salesforce/blip-image-captioning-base'
VERSION = 'blip-figure-v1'
_processor = None
_model = None


def describe(image):
    """Run the historical unconditioned 40-token configuration once per figure."""
    global _processor, _model
    started = time.perf_counter()
    with LOCK:
        if _model is None:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            _processor = BlipProcessor.from_pretrained(MODEL, local_files_only=True)
            _model = BlipForConditionalGeneration.from_pretrained(MODEL, local_files_only=True)
            _model.eval()
        loaded = time.perf_counter()
        import torch
        picture = Image.open(io.BytesIO(image)).convert('RGB')
        inputs = _processor(picture, return_tensors='pt')
        with torch.inference_mode():
            tokens = _model.generate(**inputs, max_new_tokens=40)
        caption = _processor.decode(tokens[0], skip_special_tokens=True).strip()
    if not caption:
        raise ValueError('BLIP returned an empty caption.')
    return caption, {'model': MODEL, 'version': VERSION, 'max_new_tokens': 40,
                     'load_seconds': round(loaded-started, 3),
                     'wall_seconds': round(time.perf_counter()-started, 3)}
