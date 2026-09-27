"""Structural safeguards, not a claim that generated observations are correct."""
import json
import unittest
from unittest.mock import patch
from app.services import inference


class ReflectionRegressionTests(unittest.TestCase):
    def test_unchecked_summary_cannot_certify_buddy_answer(self):
        messages = [
            {'id': 'S1', 'role': 'student', 'text': 'I am not sure.'},
            {'id': 'B1', 'role': 'buddy', 'text': 'This always works.'},
        ]
        raw = {'summary': 'The buddy is correct and the student understands everything.',
               'explained': [], 'revisit': []}
        with patch.object(inference, 'generate', return_value=(json.dumps(raw), {})):
            result, trace = inference.reflect('Topic', messages, [], 'fixture')
        self.assertNotIn(raw['summary'], result['summary'])
        self.assertIn('1 student response.', result['summary'])
        self.assertEqual(trace['raw_reflection'], json.dumps(raw))
        self.assertEqual(trace['prompt_version'], 'reflection-v2')

    def test_buddy_only_evidence_cannot_become_student_observation(self):
        messages = [{'id': 'B1', 'role': 'buddy', 'text': 'An answer.'}]
        sources = [{'id': 'P1', 'page': 1, 'text': 'Reference.'}]
        raw = {'explained': [{'observation': 'You explained this.',
                             'message_ids': ['B1'], 'source_ids': ['P1']}], 'revisit': []}
        with patch.object(inference, 'generate', return_value=(json.dumps(raw), {})):
            result, _ = inference.reflect('Topic', messages, sources, 'fixture')
        self.assertEqual(result['explained'], [])


if __name__ == '__main__':
    unittest.main()
