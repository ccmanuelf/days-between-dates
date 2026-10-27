"""SQLite storage. The database file is created at run time, never committed."""

import os
import sqlite3
from pathlib import Path

SCHEMA_VERSION = "1"


def db_path() -> Path:
    return Path(os.environ.get("DBD_DB_PATH", "data/app.db"))


def connect() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(path)


def init() -> None:
    """Create the schema and record its version, keeping a version already stored."""
    with connect() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        conn.execute(
            "INSERT OR IGNORE INTO meta (key, value) VALUES ('schema_version', ?)", (SCHEMA_VERSION,)
        )


def schema_version() -> str:
    with connect() as conn:
        row = conn.execute("SELECT value FROM meta WHERE key = 'schema_version'").fetchone()
    if row is None:
        raise LookupError("schema_version is not stored")
    return row[0]
