import sqlite3
import os
from app.config import settings


def get_db_path() -> str:
    db_dir = os.path.dirname(settings.DB_PATH)
    os.makedirs(db_dir, exist_ok=True)
    return settings.DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id TEXT PRIMARY KEY,
            uid TEXT NOT NULL,
            spot_id TEXT,
            type TEXT NOT NULL,
            original_filename TEXT,
            file_size INTEGER,
            mime_type TEXT,
            status TEXT DEFAULT 'active',
            replace_reason TEXT,
            client_ip TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_sessions (
            id TEXT PRIMARY KEY,
            created_at TEXT DEFAULT (datetime('now')),
            expires_at TEXT
        )
    """)

    conn.commit()
    conn.close()
