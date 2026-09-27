"""Workflow tests use real PDFs/SQLite and explicitly mocked model calls."""
import io
import json
import tempfile
import sqlite3
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
from app.main import create_app
from app.services.documents import extract_notes
from app.services import inference


def pdf_bytes(blank=False):
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    if not blank:
        font = DictionaryObject({NameObject('/Type'): NameObject('/Font'),
                                 NameObject('/Subtype'): NameObject('/Type1'),
                                 NameObject('/BaseFont'): NameObject('/Helvetica')})
        page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): font})})
        stream = DecodedStreamObject()
        stream.set_data(b'BT /F1 12 Tf 50 740 Td (Gradient descent) Tj 0 -24 Td '
                        b'(Gradient descent updates parameters opposite to the gradient.) Tj ET')
        page[NameObject('/Contents')] = writer._add_object(stream)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


class StudyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / 'test.db'
        self.client = TestClient(create_app(self.database))
        self.client.__enter__()
        self.sid = self.client.post('/api/sessions', json={'name': 'Gradient descent'}).json()['id']
        self.base = '/api/sessions/' + self.sid

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.temp.cleanup()

    def upload(self):
        with patch.object(inference, 'embed', side_effect=lambda chunks: [[1, 0] for _ in chunks]):
            response = self.client.post(self.base + '/documents', files={'file': ('notes.pdf', pdf_bytes(), 'application/pdf')})
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def start(self):
        self.upload()
        response = self.client.post(self.base + '/start')
        self.assertEqual(response.status_code, 200)
        return response.json()

    def send(self, request_id='one', text='We move opposite to the gradient.'):
        with patch.object(inference, 'retrieve', return_value=[{'id': 'P1C1', 'page': 1, 'text': 'Source', 'similarity': .8}]), \
                patch.object(inference, 'reply', return_value=('Could you give an example?', {'model': 'fixture'})):
            return self.client.post(self.base + '/turn', json={'text': text, 'request_id': request_id})

    def test_readable_pdf_needs_no_numbered_headings(self):
        detail = self.upload()
        self.assertEqual(detail['document']['page_count'], 1)
        self.assertIn('opposite', detail['document']['chunks'][0]['text'])
        self.assertNotIn('vectors', detail['document'])
        with TestClient(create_app(self.database)) as reopened:
            self.assertEqual(reopened.get(self.base + '/study').json()['document'], detail['document'])
            self.assertEqual(reopened.get(self.base + '/notes.pdf').content, pdf_bytes())

    def test_invalid_and_scan_pdfs_leave_session_unchanged(self):
        for data in [b'not a PDF', pdf_bytes(blank=True), b'%PDF-broken']:
            response = self.client.post(self.base + '/documents', files={'file': ('bad.pdf', data)})
            self.assertEqual(response.status_code, 422)
        self.assertIsNone(self.client.get(self.base + '/study').json()['document'])

    def test_notes_cannot_be_silently_replaced(self):
        self.upload()
        response = self.client.post(self.base + '/documents', files={'file': ('other.pdf', pdf_bytes())})
        self.assertEqual(response.status_code, 409)

    def test_session_document_isolation(self):
        self.upload()
        other = self.client.post('/api/sessions', json={'name': 'Another topic'}).json()['id']
        self.assertEqual(self.client.get('/api/sessions/' + other + '/notes.pdf').status_code, 404)
        self.assertIsNone(self.client.get('/api/sessions/' + other + '/study').json()['document'])

    def test_start_requires_notes_and_is_idempotent(self):
        self.assertEqual(self.client.post(self.base + '/start').status_code, 409)
        self.start()
        self.assertEqual(len(self.client.post(self.base + '/start').json()['messages']), 1)

    def test_failed_turn_does_not_change_history(self):
        self.start()
        with patch.object(inference, 'retrieve', side_effect=RuntimeError('offline')):
            response = self.client.post(self.base + '/turn', json={'text': 'My explanation', 'request_id': 'failure'})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(len(self.client.get(self.base + '/study').json()['messages']), 1)

    def test_retry_does_not_duplicate_messages(self):
        self.start()
        self.assertEqual(len(self.send().json()['messages']), 3)
        self.assertEqual(len(self.send().json()['messages']), 3)
        self.assertEqual(self.send(text='Different text').status_code, 409)
        with TestClient(create_app(self.database)) as restarted:
            response = restarted.post(self.base + '/turn', json={'text': 'We move opposite to the gradient.', 'request_id': 'one'})
            self.assertEqual(len(response.json()['messages']), 3)

    def test_reply_sources_persist_and_match_saved_trace(self):
        self.start()
        response = self.send().json()
        buddy_id = response['messages'][-1]['id']
        student_id = response['messages'][-2]['id']
        self.assertEqual(response['reply_sources'][buddy_id][0]['id'], 'P1C1')
        self.assertNotIn(response['messages'][0]['id'], response['reply_sources'])
        trace = self.client.get(self.base + '/export').json()['traces'][0]
        self.assertEqual(trace['buddy_message_id'], buddy_id)
        self.assertEqual(trace['student_message_id'], student_id)
        with TestClient(create_app(self.database)) as reopened:
            self.assertEqual(reopened.get(self.base + '/study').json()['reply_sources'], response['reply_sources'])

    def test_finish_and_export_and_finished_turn_rejection(self):
        self.start()
        self.assertEqual(self.client.post(self.base + '/finish').status_code, 409)
        self.send()
        with patch.object(inference, 'reflect', return_value=({'summary': 'Fixture', 'explained': [], 'revisit': []}, {})) as reflection:
            self.assertTrue(self.client.post(self.base + '/finish').json()['finished'])
            self.client.post(self.base + '/finish')
            reflection.assert_called_once()
        self.assertEqual(self.send(request_id='two').status_code, 409)
        self.assertEqual(len(self.client.get(self.base + '/export').json()['traces']), 1)

    def test_embedding_failure_does_not_save_partial_document(self):
        with patch.object(inference, 'embed', side_effect=RuntimeError('missing')):
            response = self.client.post(self.base + '/documents', files={'file': ('notes.pdf', pdf_bytes())})
        self.assertEqual(response.status_code, 503)
        self.assertIsNone(self.client.get(self.base + '/study').json()['document'])


class ReflectionValidationTests(unittest.TestCase):
    def test_version_one_session_is_preserved_by_schema_upgrade(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / 'old.db'
            with sqlite3.connect(database) as connection:
                connection.execute('CREATE TABLE study_sessions (id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)')
                connection.execute("INSERT INTO study_sessions VALUES ('existing', 'Saved topic', '2026-09-27', '2026-09-27')")
                connection.execute('PRAGMA user_version=1')
            connection.close()
            with TestClient(create_app(database)) as client:
                detail = client.get('/api/sessions/existing/study')
                self.assertEqual(detail.status_code, 200)
                self.assertEqual(detail.json()['session']['name'], 'Saved topic')
                self.assertIsNone(detail.json()['document'])

    def test_only_real_student_and_source_ids_are_accepted(self):
        messages = [{'id': 'M1', 'role': 'student', 'text': 'Actual explanation.'},
                    {'id': 'M2', 'role': 'buddy', 'text': 'A supplied answer.'}]
        sources = [{'id': 'P1C1', 'page': 1, 'text': 'Actual notes.'}]
        def item(mid, sid):
            return {'observation': 'A claim', 'message_ids': [mid], 'source_ids': [sid]}
        raw = {'summary': 'Example', 'explained': [item('M1', 'P1C1'), item('M2', 'P1C1'), item('M1', 'invented')], 'revisit': []}
        with patch.object(inference, 'generate', return_value=(json.dumps(raw), {})):
            result, _ = inference.reflect('Topic', messages, sources, 'fixture')
        self.assertEqual(len(result['explained']), 1)
        self.assertEqual(result['explained'][0]['evidence'][0]['text'], 'Actual explanation.')

    def test_invalid_pdf_size_is_rejected(self):
        with self.assertRaises(ValueError):
            extract_notes(b'%PDF-' + b'x' * (10 * 1024 * 1024), 'large.pdf')


if __name__ == '__main__':
    unittest.main()
