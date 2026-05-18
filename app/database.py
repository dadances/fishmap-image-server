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
            deleted_at TEXT,
            version INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    try:
        cursor.execute("ALTER TABLE images ADD COLUMN version INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_sessions (
            id TEXT PRIMARY KEY,
            created_at TEXT DEFAULT (datetime('now')),
            expires_at TEXT
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_images_status ON images(status)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_images_deleted_at ON images(deleted_at)
    """)

    conn.commit()
    conn.close()
