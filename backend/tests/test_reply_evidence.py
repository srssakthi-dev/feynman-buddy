"""Retrieval provenance must stay attached to the correct reply."""
import unittest
from app.services.evidence import reply_sources


class ReplyEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.messages = [
            {'id': 'opening', 'role': 'buddy'},
            {'id': 's1', 'role': 'student'}, {'id': 'b1', 'role': 'buddy'},
            {'id': 's2', 'role': 'student'}, {'id': 'b2', 'role': 'buddy'},
        ]
        self.sources = [{'id': 'P1C1', 'page': 1, 'text': 'First source'}]

    def test_explicit_ids_do_not_depend_on_trace_order(self):
        traces = [{'buddy_message_id': 'b2', 'sources': []},
                  {'buddy_message_id': 'b1', 'sources': self.sources}]
        result = reply_sources(self.messages, traces)
        self.assertEqual(result, {'b1': self.sources, 'b2': []})

    def test_legacy_sources_match_atomic_turn_order(self):
        traces = [{'sources': self.sources}, {'sources': []}]
        result = reply_sources(self.messages, traces)
        self.assertEqual(result, {'b1': self.sources, 'b2': []})
        self.assertNotIn('opening', result)

    def test_inconsistent_legacy_history_does_not_guess(self):
        self.assertEqual(reply_sources(self.messages, [{'sources': self.sources}]), {})

    def test_foreign_reply_id_is_not_exposed(self):
        self.assertEqual(reply_sources(self.messages, [
            {'buddy_message_id': 'another-session', 'sources': self.sources}]), {})


if __name__ == '__main__':
    unittest.main()
