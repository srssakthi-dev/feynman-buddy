"""Local paths. The setup checkpoint does not load any models."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.environ.get("FEYNMAN_DATA_DIR", str(PROJECT_ROOT / "data"))).resolve()
DATABASE_PATH = DATA_DIR / "sessions.sqlite3"
