"""The page's storage check, end to end: page → API → SQLite → back."""

import json
from pathlib import Path

STRINGS = json.loads((Path(__file__).resolve().parent.parent / "app/static/strings.json").read_text())


def test_an_unreadable_database_is_reported_on_the_page_at_once(tmp_path, start_server, open_page):
    # E3: the server still starts, and the page shows the storage error before any count is asked.
    db = tmp_path / "app.db"
    db.write_bytes(b"this is not a database" * 100)
    page = open_page(start_server(db).url)
    assert page.locator("#error").inner_text() == STRINGS["en"]["error_storage"]
    assert page.locator("#result").is_hidden()


def test_a_readable_database_shows_no_error(server, open_page):
    page = open_page(server.url)
    assert page.locator("#error").is_hidden()
