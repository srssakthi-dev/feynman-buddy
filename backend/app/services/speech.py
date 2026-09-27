"""Local Whisper transcription of bounded PCM WAV recordings, no FFmpeg needed."""
import io
import os
import time
import wave
from pathlib import Path
import numpy as np
from app.services.inference import LOCK

MAX_AUDIO_BYTES = 12 * 1024 * 1024
MAX_SECONDS = 60
_model = None


def decode_wav(data):
    if len(data) > MAX_AUDIO_BYTES:
        raise ValueError('Record up to 60 seconds (maximum 12 MB).')
    try:
        with wave.open(io.BytesIO(data), 'rb') as wav:
            rate, channels, width = wav.getframerate(), wav.getnchannels(), wav.getsampwidth()
            frames = wav.getnframes()
            if width != 2 or channels not in (1, 2) or not 8000 <= rate <= 48000:
                raise ValueError('Use 16-bit PCM WAV, mono or stereo, at 8-48 kHz.')
            duration = frames / rate
            if not .3 <= duration <= MAX_SECONDS:
                raise ValueError('Record between 0.3 and 60 seconds.')
            pcm = wav.readframes(frames)
            if len(pcm) != frames * channels * width:
                raise ValueError('The recording is incomplete. Please record again.')
    except (wave.Error, EOFError) as exc:
        raise ValueError('This recording is not a readable PCM WAV file.') from exc
    samples = np.frombuffer(pcm, dtype='<i2').astype(np.float32) / 32768.0
    samples = samples.reshape(-1, channels).mean(axis=1)
    if float(np.sqrt(np.mean(samples ** 2))) < .001:
        raise ValueError('The recording is silent or too quiet. Check your microphone and try again.')
    if rate != 16000:
        samples = np.interp(np.arange(round(duration * 16000)) / 16000,
                            np.arange(len(samples)) / rate, samples).astype(np.float32)
    return samples, duration


def transcribe(data):
    global _model
    samples, duration = decode_wav(data)
    started = time.perf_counter()
    # Loading a local path prevents Whisper from downloading a missing checkpoint.
    model_path = Path(os.environ.get('WHISPER_MODEL_PATH', str(Path.home() / '.cache/whisper/base.pt')))
    with LOCK:
        if _model is None:
            if not model_path.is_file():
                raise RuntimeError('The local Whisper base model is unavailable. Configure WHISPER_MODEL_PATH.')
            import whisper
            _model = whisper.load_model(str(model_path), device='cpu')
        result = _model.transcribe(samples, language='en', task='transcribe', fp16=False,
                                   temperature=0, condition_on_previous_text=False, verbose=False)
    text = result.get('text', '').strip()
    if not text:
        raise ValueError('No speech was recognised. Try again or type your explanation.')
    return text, {'model': 'whisper-base', 'language': 'en', 'duration_seconds': round(duration, 3),
                  'wall_seconds': round(time.perf_counter() - started, 3),
                  'sample_rate': 16000, 'audio_retained': False}
