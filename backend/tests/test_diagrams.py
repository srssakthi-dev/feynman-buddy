"""Isolation/approval/provenance checks with explicitly mocked AI inference."""
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from fastapi.testclient import TestClient
from app.main import create_app
from app.services import inference, vision
from test_study import pdf_bytes


def image_bytes():
    buffer = io.BytesIO()
    Image.new('RGB', (100, 60), 'white').save(buffer, format='PNG')
    return buffer.getvalue()


class DiagramTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'test.db'
        self.client = TestClient(create_app(self.path))
        self.client.__enter__()
        self.parent = self.client.post('/api/sessions', json={'name': 'Test topic'}).json()['id']
        self.base = '/api/sessions/' + self.parent
        with patch.object(inference, 'embed', return_value=[[1., 0.]]):
            self.client.post(self.base + '/documents', files={'file': ('notes.pdf', pdf_bytes())})

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.temp.cleanup()

    def create(self, page=1, data=None):
        with patch.object(vision, 'describe', return_value=('A graph.', {'model': vision.MODEL, 'wall_seconds': 1.})):
            return self.client.post(self.base + '/diagram-practices',
                data={'page': page, 'request_id': 'one'}, files={'file': ('figure.png', image_bytes() if data is None else data)})

    def test_separate_session_notes_and_retry(self):
        self.client.post(self.base + '/start')
        created = self.create()
        self.assertEqual(created.status_code, 201, created.text)
        diagram = created.json()
        sid = diagram['session']['id']
        self.assertNotEqual(sid, self.parent)
        self.assertEqual(diagram['messages'], [])
        self.assertIsNone(diagram['reflection'])
        self.assertEqual(diagram['diagram']['parent_id'], self.parent)
        self.assertEqual(self.create().json()['session']['id'], sid)
        self.assertEqual(len(self.client.get(self.base + '/study').json()['messages']), 1)
        self.assertEqual(self.client.get('/api/sessions/' + sid + '/notes.pdf').content, pdf_bytes())
        self.assertEqual(self.client.get(self.base + '/diagram.png').status_code, 404)

    def test_caption_review_required_frozen_and_persistent(self):
        sid = self.create().json()['session']['id']
        base = '/api/sessions/' + sid
        self.assertEqual(self.client.post(base + '/start').status_code, 409)
        self.assertEqual(self.client.post(base + '/diagram/approve', json={'text': '   '}).status_code, 422)
        response = self.client.post(base + '/diagram/approve', json={'text': 'A corrected description.'})
        self.assertTrue(response.json()['diagram']['edited'])
        self.assertEqual(response.json()['diagram']['original_caption'], 'A graph.')
        self.assertEqual(self.client.post(base + '/start').json()['prompt_version'], 'diagram-conversation-v1')
        self.assertEqual(self.client.post(base + '/diagram/approve', json={'text': 'Changed'}).status_code, 409)
        with TestClient(create_app(self.path)) as reopened:
            self.assertEqual(reopened.get(base + '/study').json()['diagram']['approved_caption'], 'A corrected description.')

    def test_invalid_upload_and_page_no_new_session(self):
        for page, data in [(2, None), (0, None), (1, b'not an image')]:
            self.assertEqual(self.create(page, data).status_code, 422)
        self.assertEqual(len(self.client.get('/api/sessions').json()), 1)

    def test_failed_vision_leaves_no_partial_practice(self):
        with patch.object(vision, 'describe', side_effect=RuntimeError('unavailable')):
            response = self.client.post(self.base + '/diagram-practices', data={'page': 1, 'request_id': 'fail'},
                files={'file': ('figure.png', image_bytes())})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(len(self.client.get('/api/sessions').json()), 1)

    def test_diagram_context_flows_to_turn_and_reflection(self):
        sid = self.create().json()['session']['id']
        base = '/api/sessions/' + sid
        self.client.post(base + '/diagram/approve', json={'text': 'Reviewed arrows point left.'})
        self.client.post(base + '/start')
        sources = [{'id': 'P1C1', 'page': 1, 'text': 'Notes', 'similarity': .8}]
        with patch.object(inference, 'retrieve', return_value=sources) as retrieve, \
             patch.object(inference, 'reply', return_value=('What connects them?', {})) as reply:
            result = self.client.post(base + '/turn', json={'text': 'The arrow connects these points.', 'request_id': 'turn'})
        self.assertEqual(result.status_code, 200, result.text)
        self.assertIn('Reviewed arrows', retrieve.call_args.args[1])
        self.assertEqual(reply.call_args.args[3][0]['id'], 'DIAGRAM')
        reflection = {'summary': 'Fixture', 'explained': [], 'revisit': [], 'limitations': 'Fixture'}
        with patch.object(inference, 'reflect', return_value=(reflection, {})) as reflect:
            self.assertEqual(self.client.post(base + '/finish').status_code, 200)
        self.assertIn('DIAGRAM', [s['id'] for s in reflect.call_args.args[2]])
        self.assertIsNone(self.client.get(self.base + '/study').json()['reflection'])

    def test_image_limits_and_metadata(self):
        prepared, metadata = vision.prepare_image(image_bytes())
        self.assertEqual(Image.open(io.BytesIO(prepared)).size, (100, 60))
        self.assertEqual(len(metadata['image_sha256']), 64)
        with self.assertRaises(ValueError):
            vision.prepare_image(b'x' * (vision.MAX_IMAGE_BYTES + 1))

    def test_mode_prompt_passed_to_generator(self):
        source = {'id': 'DIAGRAM', 'page': 1, 'text': 'Arrows', 'kind': 'reviewed_diagram_description'}
        with patch.object(inference, 'generate', return_value=('Question?', {})) as generate:
            answer, trace = inference.reply('Topic', [], 'Explanation', [source], 'fixture')
        self.assertIn('diagram-only', generate.call_args.args[0][0]['content'])
        self.assertEqual(trace['prompt_version'], 'diagram-conversation-v1')


if __name__ == '__main__':
    unittest.main()
