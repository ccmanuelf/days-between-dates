"""SQLite storage. The database file is created at run time, never committed.

It holds the user's own holidays, one list per calendar, and the language choice. A database that cannot be read or
written raises `StorageError`, so no caller can show a count that silently leaves the stored holidays out (SPEC, E3).
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path

SCHEMA_VERSION = "1"
LANGUAGES = ("en", "es")
BUSY_TIMEOUT = 2.0  # seconds to wait for a lock before the database counts as unwritable


class StorageError(Exception):
    """The database could not be read or written."""


class DuplicateHoliday(Exception):
    """The date is already in that calendar's list (SPEC, E2)."""


def db_path() -> Path:
    return Path(os.environ.get("DBD_DB_PATH", "data/app.db"))


def connect() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(path, timeout=BUSY_TIMEOUT)


@contextmanager
def _db():
    """One transaction; any failure to open, read or write the file becomes a StorageError."""
    try:
        conn = connect()
        try:
            with conn:
                yield conn
        finally:
            conn.close()
    except (sqlite3.Error, OSError) as error:
        raise StorageError(str(error)) from error


def init() -> None:
    """Create the schema and record its version, keeping a version already stored."""
    with _db() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        conn.execute(
            "INSERT OR IGNORE INTO meta (key, value) VALUES ('schema_version', ?)", (SCHEMA_VERSION,)
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS own_holidays ("
            "calendar TEXT NOT NULL, day TEXT NOT NULL, PRIMARY KEY (calendar, day))"
        )
        conn.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")


def schema_version() -> str:
    with _db() as conn:
        row = conn.execute("SELECT value FROM meta WHERE key = 'schema_version'").fetchone()
    if row is None:
        raise StorageError("schema_version is not stored")
    return row[0]


def add_holiday(calendar: str, day: date) -> None:
    with _db() as conn:
        try:
            conn.execute("INSERT INTO own_holidays (calendar, day) VALUES (?, ?)", (calendar, day.isoformat()))
        except sqlite3.IntegrityError as error:
            raise DuplicateHoliday(f"{day.isoformat()} is already in the {calendar} list") from error


def list_holidays(calendar: str) -> list[date]:
    with _db() as conn:
        rows = conn.execute("SELECT day FROM own_holidays WHERE calendar = ? ORDER BY day", (calendar,)).fetchall()
    return [date.fromisoformat(day) for (day,) in rows]


def remove_holiday(calendar: str, day: date) -> bool:
    """Remove a date from a calendar's list; False when it was not there."""
    with _db() as conn:
        cursor = conn.execute(
            "DELETE FROM own_holidays WHERE calendar = ? AND day = ?", (calendar, day.isoformat())
        )
    return cursor.rowcount > 0


def set_language(language: str) -> None:
    if language not in LANGUAGES:
        raise ValueError(f"unknown language: {language!r}")
    with _db() as conn:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES ('language', ?) "
            "ON CONFLICT (key) DO UPDATE SET value = excluded.value",
            (language,),
        )


def get_language() -> str | None:
    """The stored language; None when none is stored or the stored value is not one of LANGUAGES (SPEC, Q16)."""
    with _db() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = 'language'").fetchone()
    if row is None or row[0] not in LANGUAGES:
        return None
    return row[0]
