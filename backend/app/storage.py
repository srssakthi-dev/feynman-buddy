"""SQLite persistence with short-lived connections and parameterised queries."""
import sqlite3
import uuid
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class SessionStore:
    def __init__(self, database_path: Path):
        self.path = Path(database_path)

    @contextmanager
    def connection(self):
        connection = sqlite3.connect(str(self.path), timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialise(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("""
                CREATE TABLE IF NOT EXISTS study_sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            connection.execute("""CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY, session_id TEXT NOT NULL UNIQUE REFERENCES study_sessions(id),
                filename TEXT NOT NULL, page_count INTEGER NOT NULL, pdf BLOB NOT NULL,
                chunks TEXT NOT NULL, vectors TEXT NOT NULL, warnings TEXT NOT NULL
            )""")
            connection.execute("""CREATE TABLE IF NOT EXISTS practice_runs (
                session_id TEXT PRIMARY KEY REFERENCES study_sessions(id),
                model TEXT NOT NULL, prompt_version TEXT NOT NULL,
                finished INTEGER NOT NULL DEFAULT 0, reflection TEXT
            )""")
            connection.execute("""CREATE TABLE IF NOT EXISTS messages (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT NOT NULL UNIQUE, session_id TEXT NOT NULL REFERENCES study_sessions(id),
                role TEXT NOT NULL, text TEXT NOT NULL, created_at TEXT NOT NULL
            )""")
            connection.execute("""CREATE TABLE IF NOT EXISTS turn_requests (
                session_id TEXT NOT NULL REFERENCES study_sessions(id), request_id TEXT NOT NULL,
                student_text TEXT NOT NULL, trace TEXT NOT NULL,
                PRIMARY KEY (session_id, request_id)
            )""")
            connection.execute("""CREATE TABLE IF NOT EXISTS transcriptions (
                id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES study_sessions(id),
                text TEXT NOT NULL, trace TEXT NOT NULL
            )""")
            connection.execute("""CREATE TABLE IF NOT EXISTS diagrams (
                session_id TEXT PRIMARY KEY REFERENCES study_sessions(id),
                parent_id TEXT NOT NULL REFERENCES study_sessions(id), request_id TEXT NOT NULL,
                page INTEGER NOT NULL, image BLOB NOT NULL, original_caption TEXT NOT NULL,
                approved_caption TEXT, trace TEXT NOT NULL, UNIQUE(parent_id, request_id)
            )""")
            connection.execute("""CREATE TABLE IF NOT EXISTS topic_figures (
                id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES study_sessions(id),
                request_id TEXT NOT NULL, page INTEGER NOT NULL, image BLOB NOT NULL,
                original_caption TEXT NOT NULL, reviewed_caption TEXT,
                printed_caption TEXT NOT NULL, trace TEXT NOT NULL,
                UNIQUE(session_id, request_id)
            )""")
            columns = {row['name'] for row in connection.execute('PRAGMA table_info(practice_runs)')}
            if 'active_figure_id' not in columns:
                connection.execute('ALTER TABLE practice_runs ADD COLUMN active_figure_id TEXT')
            connection.execute("PRAGMA user_version=5")

    def create(self, name: str) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        session = {"id": str(uuid.uuid4()), "name": name,
                   "created_at": now, "updated_at": now}
        with self.connection() as connection:
            connection.execute(
                "INSERT INTO study_sessions (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (session["id"], name, now, now),
            )
        return session

    def list(self) -> list[dict]:
        with self.connection() as connection:
            return [dict(row) for row in connection.execute(
                "SELECT id, name, created_at, updated_at FROM study_sessions ORDER BY updated_at DESC, id"
            )]

    def get(self, session_id: str) -> dict | None:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT id, name, created_at, updated_at FROM study_sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
        return dict(row) if row else None

    def document(self, session_id, include_pdf=False):
        with self.connection() as connection:
            columns = "*" if include_pdf else "id, session_id, filename, page_count, chunks, vectors, warnings"
            row = connection.execute(f"SELECT {columns} FROM documents WHERE session_id = ?", (session_id,)).fetchone()
        if not row:
            return None
        result = dict(row)
        for field in ["chunks", "vectors", "warnings"]:
            result[field] = json.loads(result[field])
        return result

    def save_document(self, session_id, notes, data, vectors):
        with self.connection() as connection:
            connection.execute("""INSERT INTO documents
                (id, session_id, filename, page_count, pdf, chunks, vectors, warnings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (str(uuid.uuid4()), session_id, notes["filename"],
                notes["page_count"], data, json.dumps(notes["chunks"]), json.dumps(vectors), json.dumps(notes["warnings"])))

    def messages(self, session_id):
        with self.connection() as connection:
            return [dict(row) for row in connection.execute(
                "SELECT id, role, text, created_at FROM messages WHERE session_id=? ORDER BY sequence", (session_id,))]

    @staticmethod
    def add_message(connection, session_id, role, text):
        message_id = str(uuid.uuid4())
        connection.execute("INSERT INTO messages (id,session_id,role,text,created_at) VALUES (?,?,?,?,?)",
                           (message_id, session_id, role, text, datetime.now(timezone.utc).isoformat()))
        return message_id

    def run(self, session_id):
        with self.connection() as connection:
            row = connection.execute("SELECT * FROM practice_runs WHERE session_id=?", (session_id,)).fetchone()
        if not row:
            return None
        result = dict(row)
        result["reflection"] = json.loads(result["reflection"]) if result["reflection"] else None
        return result

    def start(self, session_id, model, prompt_version, opening):
        with self.connection() as connection:
            connection.execute("INSERT INTO practice_runs (session_id,model,prompt_version) VALUES (?,?,?)",
                               (session_id, model, prompt_version))
            self.add_message(connection, session_id, "buddy", opening)

    def prior_request(self, session_id, request_id):
        with self.connection() as connection:
            row = connection.execute("SELECT student_text FROM turn_requests WHERE session_id=? AND request_id=?",
                                     (session_id, request_id)).fetchone()
        return dict(row) if row else None

    def save_turn(self, session_id, request_id, student, buddy, trace):
        # Both messages and the retry record commit together only after inference succeeds.
        with self.connection() as connection:
            student_id = self.add_message(connection, session_id, "student", student)
            buddy_id = self.add_message(connection, session_id, "buddy", buddy)
            trace = {**trace, "student_message_id": student_id, "buddy_message_id": buddy_id}
            connection.execute("INSERT INTO turn_requests (session_id,request_id,student_text,trace) VALUES (?,?,?,?)",
                               (session_id, request_id, student, json.dumps(trace)))
            connection.execute("UPDATE study_sessions SET updated_at=? WHERE id=?",
                               (datetime.now(timezone.utc).isoformat(), session_id))

    def finish(self, session_id, reflection, trace):
        reflection["trace"] = trace
        with self.connection() as connection:
            connection.execute("UPDATE practice_runs SET finished=1, reflection=? WHERE session_id=?",
                               (json.dumps(reflection), session_id))

    def traces(self, session_id):
        with self.connection() as connection:
            return [json.loads(row["trace"]) for row in connection.execute(
                "SELECT trace FROM turn_requests WHERE session_id=? ORDER BY rowid", (session_id,))]

    def save_transcription(self, session_id, text, trace):
        identifier = str(uuid.uuid4())
        with self.connection() as connection:
            connection.execute('INSERT INTO transcriptions (id,session_id,text,trace) VALUES (?,?,?,?)',
                               (identifier, session_id, text, json.dumps(trace)))
        return {'id': identifier, 'text': text, 'trace': trace}

    def transcription(self, session_id, identifier):
        with self.connection() as connection:
            row = connection.execute('SELECT id,text,trace FROM transcriptions WHERE session_id=? AND id=?',
                                     (session_id, identifier)).fetchone()
        return {'id': row['id'], 'text': row['text'], 'trace': json.loads(row['trace'])} if row else None

    def diagram(self, session_id, include_image=False):
        columns = '*' if include_image else 'session_id,parent_id,request_id,page,original_caption,approved_caption,trace'
        with self.connection() as connection:
            row = connection.execute(f'SELECT {columns} FROM diagrams WHERE session_id=?', (session_id,)).fetchone()
        if not row:
            return None
        result = dict(row)
        result['trace'] = json.loads(result['trace'])
        result['edited'] = result['approved_caption'] is not None and result['approved_caption'] != result['original_caption']
        return result

    def diagram_request(self, parent_id, request_id):
        with self.connection() as connection:
            row = connection.execute('SELECT session_id FROM diagrams WHERE parent_id=? AND request_id=?',
                                     (parent_id, request_id)).fetchone()
        return row['session_id'] if row else None

    def create_diagram(self, parent_id, request_id, title, page, image, caption, trace):
        """Clone notes and create an independent practice atomically; no topic messages copied."""
        identifier = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        with self.connection() as connection:
            connection.execute('INSERT INTO study_sessions VALUES (?,?,?,?)', (identifier, title, now, now))
            connection.execute('''INSERT INTO documents
                SELECT ?, ?, filename, page_count, pdf, chunks, vectors, warnings
                FROM documents WHERE session_id=?''', (str(uuid.uuid4()), identifier, parent_id))
            connection.execute('INSERT INTO diagrams VALUES (?,?,?,?,?,?,NULL,?)',
                (identifier, parent_id, request_id, page, image, caption, json.dumps(trace)))
        return identifier

    def approve_diagram(self, session_id, caption):
        with self.connection() as connection:
            connection.execute('UPDATE diagrams SET approved_caption=? WHERE session_id=?', (caption, session_id))

    def figures(self, session_id):
        with self.connection() as connection:
            rows = connection.execute('''SELECT id,session_id,page,original_caption,
                reviewed_caption,printed_caption,trace FROM topic_figures
                WHERE session_id=? ORDER BY rowid''', (session_id,)).fetchall()
        result = [dict(row) for row in rows]
        for item in result:
            item['trace'] = json.loads(item['trace'])
            item['edited'] = (item['reviewed_caption'] is not None and
                              item['reviewed_caption'] != item['original_caption'])
        return result

    def figure(self, session_id, figure_id, include_image=False):
        columns = '*' if include_image else 'id,session_id,page,original_caption,reviewed_caption,printed_caption,trace'
        with self.connection() as connection:
            row = connection.execute(f'SELECT {columns} FROM topic_figures WHERE session_id=? AND id=?',
                                     (session_id, figure_id)).fetchone()
        if not row:
            return None
        result = dict(row)
        result['trace'] = json.loads(result['trace'])
        return result

    def figure_request(self, session_id, request_id):
        with self.connection() as connection:
            row = connection.execute('SELECT id FROM topic_figures WHERE session_id=? AND request_id=?',
                                     (session_id, request_id)).fetchone()
        return row['id'] if row else None

    def save_figure(self, session_id, request_id, page, image, caption, printed_caption, trace):
        figure_id = str(uuid.uuid4())
        with self.connection() as connection:
            connection.execute('''INSERT INTO topic_figures
                (id,session_id,request_id,page,image,original_caption,printed_caption,trace)
                VALUES (?,?,?,?,?,?,?,?)''',
                (figure_id, session_id, request_id, page, image, caption, printed_caption, json.dumps(trace)))
        return figure_id

    def review_figure(self, session_id, figure_id, caption):
        with self.connection() as connection:
            connection.execute('''UPDATE topic_figures SET reviewed_caption=?
                WHERE session_id=? AND id=?''', (caption, session_id, figure_id))

    def select_figure(self, session_id, figure_id):
        """Change conversation context without fabricating a buddy reply."""
        with self.connection() as connection:
            connection.execute('UPDATE practice_runs SET active_figure_id=? WHERE session_id=?',
                               (figure_id, session_id))


def figure_source(figure):
    return {'id': 'FIGURE-' + figure['id'], 'page': figure['page'],
            'kind': 'reviewed_figure_description', 'text': figure['reviewed_caption'],
            'printed_caption': figure['printed_caption'], 'similarity': None,
            'selection': 'Selected figure context; not similarity-ranked.',
            'provenance': 'BLIP description reviewed by the student; image not independently verified by buddy.'}
