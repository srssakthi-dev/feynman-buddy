"""Selected figures enter the original topic session only after review."""
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from fastapi.testclient import TestClient
from app.main import create_app
from app.services import blip, inference
from test_study import pdf_bytes


def image_bytes():
    buffer = io.BytesIO()
    Image.new('RGB', (180, 100), 'white').save(buffer, 'PNG')
    return buffer.getvalue()


class TopicFigureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / 'study.sqlite3'
        self.client = TestClient(create_app(self.database))
        self.client.__enter__()
        self.sid = self.client.post('/api/sessions', json={'name': 'Gradient descent'}).json()['id']
        self.base = f'/api/sessions/{self.sid}'

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.temp.cleanup()

    def notes(self):
        with patch.object(inference, 'embed', return_value=[[1., 0.]]):
            response = self.client.post(self.base + '/documents',
                files={'file': ('notes.pdf', pdf_bytes(), 'application/pdf')})
        self.assertEqual(response.status_code, 201, response.text)

    def figure(self, page=1, request_id='one', data=None):
        with patch.object(blip, 'describe', return_value=('a graph with a line going up and down',
                            {'model': blip.MODEL, 'wall_seconds': 4.})) as caption:
            response = self.client.post(self.base + '/figures', data={
                'page': page, 'request_id': request_id, 'printed_caption': 'Illustrative update'},
                files={'file': ('figure.png', image_bytes() if data is None else data, 'image/png')})
        return response, caption

    def test_upload_is_scoped_retryable_and_independent_of_child_diagrams(self):
        self.assertEqual(self.figure()[0].status_code, 409)
        self.notes()
        self.assertEqual(self.figure(page=2)[0].status_code, 422)
        self.assertEqual(self.figure(data=b'fake')[0].status_code, 422)
        first, caption = self.figure()
        self.assertEqual(first.status_code, 201, first.text)
        caption.assert_called_once()
        figure = first.json()['figures'][0]
        self.assertIsNone(figure['reviewed_caption'])
        self.assertEqual(figure['printed_caption'], 'Illustrative update')
        self.assertNotIn('image', figure)
        retry, caption = self.figure()
        self.assertEqual(retry.status_code, 201)
        caption.assert_not_called()
        self.assertEqual(len(retry.json()['figures']), 1)
        self.assertEqual(self.client.get(f'{self.base}/figures/{figure["id"]}/image.png').status_code, 200)
        other = self.client.post('/api/sessions', json={'name': 'Other'}).json()['id']
        self.assertEqual(self.client.get(f'/api/sessions/{other}/figures/{figure["id"]}/image.png').status_code, 404)

    def test_same_conversation_review_activation_and_return(self):
        self.notes()
        self.client.post(self.base + '/start')
        fid = self.figure()[0].json()['figures'][0]['id']
        self.assertEqual(self.client.post(f'{self.base}/figures/{fid}/discuss').status_code, 409)
        reviewed = self.client.post(f'{self.base}/figures/{fid}/review', json={'text': 'B is below A; arrows oppose.'})
        self.assertEqual(reviewed.status_code, 200)
        active = self.client.post(f'{self.base}/figures/{fid}/discuss').json()
        self.assertEqual(active['session']['id'], self.sid)
        self.assertEqual(active['active_figure_id'], fid)
        self.assertEqual(len(active['messages']), 1)
        with patch.object(inference, 'retrieve', return_value=[{'id':'P1C1','page':1,'text':'Notes','similarity':.8}]), \
             patch.object(inference, 'reply', return_value=('How do they connect?', {'model':'fixture'})) as reply:
            response = self.client.post(self.base + '/turn', json={'text': 'Arrows point opposite ways.', 'request_id': 'turn-one'})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(reply.call_args.args[3][0]['kind'], 'reviewed_figure_description')
        self.assertEqual(response.json()['reply_sources'][response.json()['messages'][-1]['id']][0]['id'], 'FIGURE-' + fid)
        self.assertEqual(self.client.post(f'{self.base}/figures/{fid}/review', json={'text': 'Changed'}).status_code, 409)
        returned = self.client.post(self.base + '/figures/return-to-topic').json()
        self.assertIsNone(returned['active_figure_id'])
        self.assertEqual(returned['session']['id'], self.sid)
        self.assertEqual([m['role'] for m in returned['messages']], ['buddy','student','buddy'])
        reopened_figure = self.client.post(f'{self.base}/figures/{fid}/discuss').json()
        self.assertEqual(len(reopened_figure['messages']), len(returned['messages']))
        with TestClient(create_app(self.database)) as reopened:
            self.assertEqual(reopened.get(self.base + '/study').json()['figures'][0]['reviewed_caption'],
                             'B is below A; arrows oppose.')

    def test_relevant_figure_is_offered_and_reflection_sees_it_only_if_discussed(self):
        self.notes()
        fid = self.figure()[0].json()['figures'][0]['id']
        self.client.post(f'{self.base}/figures/{fid}/review', json={'text': 'B is below A.'})
        self.client.post(self.base + '/start')
        with patch.object(inference, 'retrieve', return_value=[{'id':'P1C1','page':1,'text':'Notes','similarity':.8}]), \
             patch.object(inference, 'reply', return_value=('Would you like to use the figure?', {})) as reply:
            self.client.post(self.base + '/turn', json={'text': 'It lowers loss.', 'request_id': 'ordinary'})
        self.assertEqual(reply.call_args.kwargs['available_figures'][0]['id'], fid)
        self.assertEqual(reply.call_args.args[3][0]['id'], 'P1C1')
        reflection = {'summary':'fixture','explained':[],'revisit':[],'limitations':'fixture'}
        with patch.object(inference, 'reflect', return_value=(reflection, {})) as reflect:
            self.assertEqual(self.client.post(self.base + '/finish').status_code, 200)
        self.assertNotIn('FIGURE-' + fid, [source['id'] for source in reflect.call_args.args[2]])

    def test_explicit_figure_request_selects_single_attached_image(self):
        self.notes()
        fid = self.figure()[0].json()['figures'][0]['id']
        self.client.post(f'{self.base}/figures/{fid}/review', json={'text': 'A loss curve with two labelled points.'})
        self.client.post(self.base + '/start')
        with patch.object(inference, 'retrieve', return_value=[{'id':'P2C1','page':2,'text':'Other page','similarity':.8}]), \
             patch.object(inference, 'reply', return_value=('Select the attached figure to explain it.', {})) as reply:
            response = self.client.post(self.base + '/turn', json={'text': 'I want to explain the diagram.', 'request_id': 'figure-request'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(reply.call_args.kwargs['available_figures'], [])
        self.assertEqual(reply.call_args.args[3][0]['id'], 'FIGURE-' + fid)
        self.assertEqual(response.json()['active_figure_id'], fid)
        self.assertEqual(response.json()['messages'][-1]['text'], 'Select the attached figure to explain it.')
        self.assertEqual(len(response.json()['messages']), 3)

    def test_figure_prompts_distinguish_selected_from_available(self):
        figure = {'id':'FIGURE-1','page':1,'kind':'reviewed_figure_description',
                  'text':'B is below A.','similarity':None}
        with patch.object(inference, 'generate', return_value=('Question?', {})) as generate:
            _, trace = inference.reply('Topic', [], 'Here is my explanation', [figure], 'fixture')
        self.assertIn('cannot see or independently verify the image pixels', generate.call_args.args[0][0]['content'])
        self.assertIn('Do not ask them to select it again', generate.call_args.args[0][0]['content'])
        self.assertEqual(trace['figure_prompt_version'], 'figure-selected-v3')
        with patch.object(inference, 'generate', return_value=('Question?', {})) as generate:
            inference.reply('Topic', [], 'Here is my explanation', [], 'fixture',
                            available_figures=[{'id':'1','page':1,'description':'A graph'}])
        self.assertIn('available_figures', generate.call_args.args[0][0]['content'])
        self.assertIn('Never say a listed figure is missing or unavailable', generate.call_args.args[0][0]['content'])
        self.assertNotIn('Do not ask them to select it again', generate.call_args.args[0][0]['content'])


if __name__ == '__main__':
    unittest.main()
