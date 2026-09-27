"""Real SQLite/API verification; these tests do not measure model quality."""
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import create_app


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / "test.sqlite3"
        self.client = TestClient(create_app(self.database))
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.temp.cleanup()

    def test_create_and_retrieve_normalised_topic(self):
        response = self.client.post("/api/sessions", json={"name": "  Gradient   descent  "})
        self.assertEqual(response.status_code, 201)
        session = response.json()
        self.assertEqual(session["name"], "Gradient descent")
        self.assertEqual(self.client.get("/api/sessions/" + session["id"]).json(), session)
        self.assertEqual(self.client.get("/api/sessions").json(), [session])

    def test_sessions_survive_application_restart(self):
        session = self.client.post("/api/sessions", json={"name": "Gradient descent"}).json()
        with TestClient(create_app(self.database)) as restarted:
            self.assertEqual(restarted.get("/api/sessions/" + session["id"]).json(), session)

    def test_invalid_names_are_rejected(self):
        for name in ["", "   ", "x" * 101, None, 123]:
            with self.subTest(name=name):
                self.assertEqual(self.client.post("/api/sessions", json={"name": name}).status_code, 422)
        self.assertEqual(self.client.get("/api/sessions").json(), [])

    def test_same_topic_can_have_separate_practice_sessions(self):
        first = self.client.post("/api/sessions", json={"name": "Gradient descent"}).json()
        second = self.client.post("/api/sessions", json={"name": "Gradient descent"}).json()
        self.assertNotEqual(first["id"], second["id"])

    def test_missing_session_returns_404(self):
        self.assertEqual(self.client.get("/api/sessions/not-a-session").status_code, 404)

    def test_names_are_data_not_sql(self):
        name = "Loss'); DROP TABLE study_sessions; --"
        self.assertEqual(self.client.post("/api/sessions", json={"name": name}).status_code, 201)
        self.assertEqual(self.client.get("/api/sessions").json()[0]["name"], name)


if __name__ == "__main__":
    unittest.main()
