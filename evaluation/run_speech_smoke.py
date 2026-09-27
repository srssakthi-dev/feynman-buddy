"""Real local ASR via the API; synthetic voice fixture, not a human speech study."""
import json
import re
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import create_app
from app.storage import SessionStore

root = Path(__file__).resolve().parents[1]
expected = 'A set is an unordered collection of distinct elements. The intersection contains elements shared by both sets.'
audio = root / '.local/speech-evaluation/sets.wav'
with tempfile.TemporaryDirectory() as temporary:
    database = Path(temporary) / 'speech.db'
    with TestClient(create_app(database)) as client:
        store = SessionStore(database)
        session = store.create('Sets ASR development fixture')['id']
        store.start(session, 'not-invoked', 'conversation-v2', 'Explain sets.')
        response = client.post(f'/api/sessions/{session}/transcribe', files={'file': ('sets.wav', audio.read_bytes(), 'audio/wav')})
        result = {'kind': 'synthetic-speech API integration check', 'expected': expected,
                  'fixture': 'Windows System.Speech synthetic voice, 16 kHz mono PCM WAV',
                  'status_code': response.status_code, 'response': response.json(),
                  'messages_after_transcription': len(store.messages(session)),
                  'limitations': 'One synthetic recording. No browser microphone, accent/noise study, ASR candidate comparison or playback-audibility verification.'}
        if response.status_code == 200:
            result['normalised_exact_match'] = re.findall(r"\w+", expected.lower()) == re.findall(r"\w+", response.json()['text'].lower())
        output = root / 'evaluation/results/speech_smoke_v1.json'
        output.write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))
