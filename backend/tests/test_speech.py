"""Real WAV decoding and API state checks; model calls mocked here."""
import io
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch
from unittest.mock import Mock
import numpy as np
from fastapi.testclient import TestClient
from app.main import create_app
from app.storage import SessionStore
from app.services import speech, inference


def wav_bytes(seconds=1, rate=16000, channels=1, silent=False):
    samples = np.zeros(round(rate * seconds)) if silent else np.sin(np.arange(round(rate * seconds)) * 2 * np.pi * 220 / rate) * .2
    pcm = np.repeat((samples * 32767).astype('<i2')[:, None], channels, axis=1).tobytes()
    target = io.BytesIO()
    with wave.open(target, 'wb') as wav:
        wav.setnchannels(channels); wav.setsampwidth(2); wav.setframerate(rate); wav.writeframes(pcm)
    return target.getvalue()


class SpeechDecodingTests(unittest.TestCase):
    def test_stereo_resampling_produces_mono_16khz(self):
        samples, duration = speech.decode_wav(wav_bytes(rate=22050, channels=2))
        self.assertEqual(len(samples), 16000)
        self.assertEqual(samples.dtype, np.float32)
        self.assertEqual(duration, 1)

    def test_rejects_silence_corruption_and_duration_limits(self):
        for data in [b'invalid', wav_bytes(silent=True), wav_bytes(seconds=.1), wav_bytes(seconds=61), wav_bytes()[:-20]]:
            with self.subTest(size=len(data)), self.assertRaises(ValueError):
                speech.decode_wav(data)

    def test_missing_local_model_does_not_download(self):
        with patch.object(speech, '_model', None), patch.dict('os.environ', {'WHISPER_MODEL_PATH': 'missing-test-model.pt'}):
            with self.assertRaises(RuntimeError):
                speech.transcribe(wav_bytes())

    def test_waveform_and_cpu_settings_reach_model(self):
        model = Mock()
        model.transcribe.return_value = {'text': ' A set has elements. '}
        with patch.object(speech, '_model', model):
            text, trace = speech.transcribe(wav_bytes())
        self.assertEqual(text, 'A set has elements.')
        self.assertEqual(model.transcribe.call_args.args[0].shape, (16000,))
        self.assertFalse(model.transcribe.call_args.kwargs['fp16'])
        self.assertEqual(model.transcribe.call_args.kwargs['language'], 'en')
        self.assertFalse(trace['audio_retained'])


class SpeechWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / 'sessions.db'
        self.client = TestClient(create_app(self.db)); self.client.__enter__()
        self.store = SessionStore(self.db)
        self.sid = self.store.create('Sets')['id']
        self.base = '/api/sessions/' + self.sid
        self.store.start(self.sid, 'fixture', 'conversation-v2', 'Teach me about sets.')

    def tearDown(self):
        self.client.__exit__(None, None, None); self.temp.cleanup()

    def transcribe(self):
        with patch.object(speech, 'transcribe', return_value=('A set has distinct elements.', {'model': 'fixture', 'audio_retained': False})):
            return self.client.post(self.base + '/transcribe', files={'file': ('recording.wav', wav_bytes(), 'audio/wav')})

    def test_transcription_does_not_send_a_message(self):
        response = self.transcribe()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.store.messages(self.sid)), 1)
        transcript = self.store.transcription(self.sid, response.json()['id'])
        self.assertEqual(transcript['text'], 'A set has distinct elements.')
        self.assertFalse(transcript['trace']['audio_retained'])

    def test_reviewed_text_enters_normal_turn_and_preserves_original(self):
        identifier = self.transcribe().json()['id']
        revised = 'A set is an unordered collection of distinct elements.'
        with patch.object(inference, 'retrieve', return_value=[]), patch.object(inference, 'reply', return_value=('Does order matter?', {})) as reply:
            result = self.client.post(self.base + '/turn', json={'text': revised, 'request_id': 'edited', 'transcription_id': identifier})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(reply.call_args.args[2], revised)
        trace = self.store.traces(self.sid)[0]
        self.assertEqual(trace['transcription']['text'], 'A set has distinct elements.')
        self.assertTrue(trace['transcription']['edited_before_send'])

    def test_other_session_transcript_is_rejected(self):
        other = self.store.create('Other')['id']
        identifier = self.store.save_transcription(other, 'Private transcript', {})['id']
        result = self.client.post(self.base + '/turn', json={'text': 'Explanation', 'request_id': 'bad', 'transcription_id': identifier})
        self.assertEqual(result.status_code, 422)
        self.assertEqual(len(self.store.messages(self.sid)), 1)

    def test_finished_session_and_invalid_audio_do_not_write(self):
        result = self.client.post(self.base + '/transcribe', files={'file': ('bad.wav', b'bad')})
        self.assertEqual(result.status_code, 422)
        self.store.finish(self.sid, {}, {})
        self.assertEqual(self.transcribe().status_code, 409)


if __name__ == '__main__':
    unittest.main()
