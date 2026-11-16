"""The page's storage check, end to end: page → API → SQLite → back."""

import sqlite3

from playwright.sync_api import expect

from test_page import STRINGS, add_holiday


def test_an_unreadable_database_is_reported_on_the_page_at_once(tmp_path, start_server, open_page):
    # E3: the server still starts, and the page shows the storage error before any count is asked.
    db = tmp_path / "app.db"
    db.write_bytes(b"this is not a database" * 100)
    page = open_page(start_server(db).url)
    expect(page.locator("#error")).to_have_text(STRINGS["en"]["error_storage"])
    expect(page.locator("#result")).to_be_hidden()
    expect(page.locator("#storage-status")).to_have_text(STRINGS["en"]["storage_down"])  # the app bar says so too


def test_a_readable_database_shows_no_error(server, open_page):
    page = open_page(server.url)
    expect(page.locator("#error")).to_be_hidden()
    expect(page.locator("#storage-status")).to_have_text(STRINGS["en"]["storage_ok"])


def test_the_storage_status_is_an_icon_and_a_word(server, open_page):
    """The visual standard's rule 2: every status shows an icon and a word, never color alone."""
    page = open_page(server.url)
    chip = page.locator("#storage-status")
    expect(chip).to_have_text(STRINGS["en"]["storage_ok"])
    expect(chip.locator("svg")).to_have_count(1)


def test_the_storage_status_comes_back_once_storage_answers_again(server, open_page):
    """A refused write shows "Storage unavailable"; the next write that the database accepts shows "Storage OK" again,
    so the app bar never keeps a status that is no longer true."""
    page = open_page(server.url)
    lock = sqlite3.connect(server.db, isolation_level=None)
    lock.execute("BEGIN IMMEDIATE")  # another writer holds the database: no write can take place
    try:
        add_holiday(page, "2026-10-28")
        expect(page.locator("#storage-status")).to_have_text(STRINGS["en"]["storage_down"])
    finally:
        lock.execute("ROLLBACK")
        lock.close()
    add_holiday(page, "2026-10-29")
    expect(page.locator("#storage-status")).to_have_text(STRINGS["en"]["storage_ok"])
