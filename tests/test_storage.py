"""Unit tests of storage against a real SQLite file (plan step 4). They do not count toward done: the scenarios count
through the API and the page, with a server restart between write and read, once steps 5 and 6 wire storage in."""

import sqlite3
from datetime import date

import pytest

from app import storage

D = date.fromisoformat


@pytest.fixture
def db(tmp_path, monkeypatch):
    path = tmp_path / "app.db"
    monkeypatch.setenv("DBD_DB_PATH", str(path))
    monkeypatch.setattr(storage, "BUSY_TIMEOUT", 0.2)
    storage.init()
    return path


def test_s5_an_own_holiday_is_stored_in_its_calendar_and_read_back(db):
    storage.add_holiday("us", D("2026-10-28"))
    assert storage.list_holidays("us") == [D("2026-10-28")]
    with sqlite3.connect(db) as conn:  # it is in the file, not only in memory
        assert conn.execute("SELECT calendar, day FROM own_holidays").fetchall() == [("us", "2026-10-28")]


def test_s6_a_holiday_stays_in_its_calendar(db):
    storage.add_holiday("us", D("2026-10-28"))
    assert storage.list_holidays("mx") == []


def test_s7_a_removed_holiday_is_no_longer_listed(db):
    storage.add_holiday("us", D("2026-10-28"))
    assert storage.remove_holiday("us", D("2026-10-28")) is True
    assert storage.list_holidays("us") == []
    assert storage.remove_holiday("us", D("2026-10-28")) is False


def test_e2_a_duplicate_is_refused_and_the_list_is_unchanged(db):
    storage.add_holiday("us", D("2026-10-28"))
    with pytest.raises(storage.DuplicateHoliday):
        storage.add_holiday("us", D("2026-10-28"))
    assert storage.list_holidays("us") == [D("2026-10-28")]
    storage.add_holiday("mx", D("2026-10-28"))  # the same date in the other calendar is not a duplicate
    assert storage.list_holidays("mx") == [D("2026-10-28")]


def test_the_list_is_in_date_order_across_the_years_accepted(db):
    for iso in ("9999-12-31", "0001-01-01", "2026-10-28"):
        storage.add_holiday("mx", D(iso))
    assert storage.list_holidays("mx") == [D("0001-01-01"), D("2026-10-28"), D("9999-12-31")]


def test_the_language_choice_is_stored(db):
    assert storage.get_language() is None
    storage.set_language("es")
    assert storage.get_language() == "es"
    storage.set_language("en")
    assert storage.get_language() == "en"


def test_an_unknown_language_is_refused_and_nothing_is_stored(db):
    with pytest.raises(ValueError):
        storage.set_language("fr")
    assert storage.get_language() is None


def test_a_stored_language_that_cannot_be_read_counts_as_none(db):
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO settings (key, value) VALUES ('language', 'xx')")
    assert storage.get_language() is None


def test_e3_an_unreadable_database_raises_on_every_call(tmp_path, monkeypatch):
    path = tmp_path / "app.db"
    path.write_bytes(b"this is not a database" * 100)
    monkeypatch.setenv("DBD_DB_PATH", str(path))
    for call in (
        storage.init,
        lambda: storage.list_holidays("us"),
        lambda: storage.add_holiday("us", D("2026-10-28")),
        lambda: storage.remove_holiday("us", D("2026-10-28")),
        storage.get_language,
        lambda: storage.set_language("es"),
    ):
        with pytest.raises(storage.StorageError):
            call()


def test_e3_an_unwritable_database_raises_on_writes_and_still_reads(db):
    storage.add_holiday("us", D("2026-10-28"))
    lock = sqlite3.connect(db, isolation_level=None)
    lock.execute("BEGIN IMMEDIATE")  # another writer holds the database: no write can take place
    try:
        with pytest.raises(storage.StorageError):
            storage.add_holiday("us", D("2026-10-29"))
        with pytest.raises(storage.StorageError):
            storage.set_language("es")
        assert storage.list_holidays("us") == [D("2026-10-28")]
    finally:
        lock.execute("ROLLBACK")
        lock.close()
    assert storage.list_holidays("us") == [D("2026-10-28")]
