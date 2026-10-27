"""The thin path, end to end: page → API → SQLite → back."""

import sqlite3

from playwright.sync_api import expect


def test_page_shows_what_sqlite_holds(server, page):
    # The app wrote the schema version at startup; the page reads it back through the API.
    page.goto(server["url"])
    expect(page.locator("#status")).to_have_text("Storage: ok, schema 1")

    # Change the stored value behind the app's back: the page must show the new one, so it is read, not hard-coded.
    with sqlite3.connect(server["db"]) as conn:
        conn.execute("UPDATE meta SET value = 'marker-7f3a' WHERE key = 'schema_version'")
    page.reload()
    expect(page.locator("#status")).to_have_text("Storage: ok, schema marker-7f3a")


def test_an_unreadable_database_is_reported_on_the_page(tmp_path, start_server, page):
    # E3: the server still starts, and the page shows the storage error instead of a result.
    db = tmp_path / "app.db"
    db.write_bytes(b"this is not a database" * 100)
    page.goto(start_server(db))
    expect(page.locator("#status")).to_have_text("Storage error: HTTP 503")
