import sqlite3
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parents[3]

# Database location
DATABASE_PATH = BASE_DIR / "data" / "support_ticket_classifier.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection