"""The scenarios through the API on the running server (plan step 5). The page tests of step 6 are the ones that
count for the scenarios; these support them and pin each route's behaviour."""

import sqlite3

import pytest

from app.main import STORAGE_MESSAGE
from test_page import STRINGS

US_RANGE = "calendar=us&start=2026-10-26&end=2026-10-30"  # Monday to Friday, no US holiday


def business(server, query):
    status, body = server.call("GET", f"/api/count?{query}")
    assert status == 200, body
    return (body["business"]["start_not_counted"], body["business"]["both_counted"])


def test_s4_switching_calendar_recomputes(server):
    # Wednesday 11 November 2026 is Veterans Day in the US calendar and no rest day in Mexico's.
    week = "start=2026-11-09&end=2026-11-13"
    assert business(server, f"calendar=mx&{week}") == (4, 5)
    assert business(server, f"calendar=us&{week}") == (3, 4)


def test_s5_an_own_holiday_is_stored_and_survives_a_restart(server):
    assert business(server, US_RANGE) == (4, 5)
    status, body = server.call("POST", "/api/holidays", {"calendar": "us", "day": "2026-10-28"})
    assert (status, body) == (201, {"calendar": "us", "day": "2026-10-28"})
    assert business(server, US_RANGE) == (3, 4)
    server.restart()
    assert server.call("GET", "/api/holidays?calendar=us") == (200, {"calendar": "us", "holidays": ["2026-10-28"]})
    assert business(server, US_RANGE) == (3, 4)


def test_s6_a_holiday_stays_in_its_calendar(server):
    assert server.call("POST", "/api/holidays", {"calendar": "us", "day": "2026-10-28"})[0] == 201
    assert server.call("GET", "/api/holidays?calendar=us")[1]["holidays"] == ["2026-10-28"]
    assert server.call("GET", "/api/holidays?calendar=mx") == (200, {"calendar": "mx", "holidays": []})
    assert business(server, "calendar=mx&start=2026-10-26&end=2026-10-30") == (4, 5)


def test_s7_a_removed_holiday_is_gone_also_after_a_restart(server):
    server.call("POST", "/api/holidays", {"calendar": "us", "day": "2026-10-28"})
    assert server.call("DELETE", "/api/holidays/us/2026-10-28") == (204, None)
    assert business(server, US_RANGE) == (4, 5)
    server.restart()
    assert server.call("GET", "/api/holidays?calendar=us")[1]["holidays"] == []
    assert business(server, US_RANGE) == (4, 5)
    status, body = server.call("DELETE", "/api/holidays/us/2026-10-28")
    assert status == 404 and body["error"]["code"] == "not_found"


@pytest.mark.parametrize(
    "day",
    ["2026-10-31", "2026-11-01", "2026-12-25"],  # a Saturday, a Sunday, a built-in holiday of both calendars
)
def test_s8_a_day_is_excluded_once(server, day):
    query = "calendar=us&start=2026-10-26&end=2026-12-31"
    before = business(server, query)
    server.call("POST", "/api/holidays", {"calendar": "us", "day": day})
    assert business(server, query) == before


def test_s9_the_past_years_flag(server):
    _, past = server.call("GET", "/api/count?calendar=mx&start=2000-01-03&end=2026-10-30")
    _, future = server.call("GET", "/api/count?calendar=mx&start=2150-01-05&end=2150-01-09")
    assert past["past_years"] is True and future["past_years"] is False


@pytest.mark.parametrize(
    "query,field,code",
    [
        ("calendar=mx&end=2026-10-30", "start", "required"),
        ("calendar=mx&start=&end=2026-10-30", "start", "required"),
        ("calendar=mx&start=2026-02-30&end=2026-10-30", "start", "invalid_date"),
        ("calendar=mx&start=2026-10-26&end=0000-01-01", "end", "invalid_date"),
        ("calendar=mx&start=2026-10-26&end=10000-01-01", "end", "invalid_date"),
        ("calendar=mx&start=1949-12-31&end=2026-10-30", "start", "invalid_date"),
        ("calendar=mx&start=2026-10-26&end=2151-01-01", "end", "invalid_date"),
        ("calendar=mx&start=26/10/2026&end=2026-10-30", "start", "invalid_date"),
        ("calendar=xx&start=2026-10-26&end=2026-10-30", "calendar", "unknown_calendar"),
    ],
)
def test_e1_invalid_input_is_refused_naming_the_field(server, query, field, code):
    status, body = server.call("GET", f"/api/count?{query}")
    assert status == 422
    assert (body["error"]["field"], body["error"]["code"]) == (field, code)
    assert field in body["error"]["message"]
    assert "total" not in body and "business" not in body


@pytest.mark.parametrize("day", ["", "2026-02-30", "2026-13-01", "tomorrow", "1949-12-31", "2151-01-01"])
def test_e1_an_invalid_holiday_is_refused_and_nothing_is_stored(server, day):
    status, body = server.call("POST", "/api/holidays", {"calendar": "us", "day": day})
    assert status == 422 and body["error"]["field"] == "day"
    with sqlite3.connect(server.db) as conn:  # read the database itself after the refusal
        assert conn.execute("SELECT COUNT(*) FROM own_holidays").fetchone() == (0,)


def test_the_years_accepted_are_1950_to_2150(server):
    """The owner's decision of 2026-11-15 (SPEC, Expectations): the first and last dates accepted count and store; the
    days just outside are refused, and the message names the years."""
    status, body = server.call("GET", "/api/count?calendar=mx&start=1950-01-01&end=2150-12-31")
    assert status == 200, body
    assert server.call("POST", "/api/holidays", {"calendar": "mx", "day": "1950-01-01"})[0] == 201
    assert server.call("POST", "/api/holidays", {"calendar": "mx", "day": "2150-12-31"})[0] == 201
    for query in ("start=1949-12-31&end=1950-01-01", "start=2150-12-31&end=2151-01-01"):
        status, body = server.call("GET", f"/api/count?calendar=mx&{query}")
        assert status == 422 and body["error"]["code"] == "invalid_date"
        assert "1950" in body["error"]["message"] and "2150" in body["error"]["message"]


def test_a_day_stored_outside_the_years_accepted_can_still_be_removed(server):
    """A database from before 2026-11-15 may hold an own holiday outside 1950 to 2150: it is listed, and removing it
    works."""
    with sqlite3.connect(server.db) as conn:
        conn.execute("INSERT INTO own_holidays (calendar, day) VALUES ('mx', '1949-12-31')")
    assert server.call("GET", "/api/holidays?calendar=mx")[1]["holidays"] == ["1949-12-31"]
    assert server.call("DELETE", "/api/holidays/mx/1949-12-31")[0] == 204
    assert server.call("GET", "/api/holidays?calendar=mx")[1]["holidays"] == []


@pytest.mark.parametrize("language", ["en", "es"])
def test_the_page_names_the_years_accepted_in_each_language(language):
    text = STRINGS[language]["error_invalid_date"]
    assert "1950" in text and "2150" in text and "9999" not in text


@pytest.mark.parametrize("body,field,code", [
    ({"calendar": "us", "day": 20261028}, "day", "invalid_date"),
    ({"calendar": "us", "day": ["2026-10-28"]}, "day", "invalid_date"),
    ({"calendar": ["us"], "day": "2026-10-28"}, "calendar", "unknown_calendar"),
    ({"calendar": {"us": True}, "day": "2026-10-28"}, "calendar", "unknown_calendar"),
], ids=["day-number", "day-list", "calendar-list", "calendar-object"])
def test_e1_a_value_that_is_not_text_is_refused_naming_the_field(server, body, field, code):
    status, answer = server.call("POST", "/api/holidays", body)
    assert status == 422 and (answer["error"]["field"], answer["error"]["code"]) == (field, code)
    with sqlite3.connect(server.db) as conn:  # read the database itself after the refusal
        assert conn.execute("SELECT COUNT(*) FROM own_holidays").fetchone() == (0,)


def test_e2_a_duplicate_is_refused_and_the_list_is_unchanged(server):
    server.call("POST", "/api/holidays", {"calendar": "us", "day": "2026-10-28"})
    status, body = server.call("POST", "/api/holidays", {"calendar": "us", "day": "2026-10-28"})
    assert status == 409 and (body["error"]["code"], body["error"]["field"]) == ("duplicate", "day")
    assert server.call("GET", "/api/holidays?calendar=us")[1]["holidays"] == ["2026-10-28"]


def test_e3_an_unreadable_database_gives_no_count(tmp_path, start_server):
    db = tmp_path / "app.db"
    db.write_bytes(b"this is not a database" * 100)
    server = start_server(db)
    for method, path, body in [
        ("GET", f"/api/count?{US_RANGE}", None),
        ("GET", "/api/holidays?calendar=us", None),
        ("POST", "/api/holidays", {"calendar": "us", "day": "2026-10-28"}),
        ("GET", "/api/language", None),
        ("PUT", "/api/language", {"language": "es"}),
    ]:
        status, answer = server.call(method, path, body)
        assert status == 503, (method, path)
        assert answer == {"error": {"code": "storage", "field": None, "message": STORAGE_MESSAGE}}


def test_e3_an_unwritable_database_refuses_writes_and_still_counts(server):
    lock = sqlite3.connect(server.db, isolation_level=None)
    lock.execute("BEGIN IMMEDIATE")  # another writer holds the database: no write can take place
    try:
        assert server.call("POST", "/api/holidays", {"calendar": "us", "day": "2026-10-28"})[0] == 503
        assert server.call("PUT", "/api/language", {"language": "es"})[0] == 503
        assert business(server, US_RANGE) == (4, 5)  # reading still works, and nothing was added
    finally:
        lock.execute("ROLLBACK")
        lock.close()


def test_the_language_choice_is_stored_and_survives_a_restart(server):
    assert server.call("GET", "/api/language") == (200, {"language": None})
    assert server.call("PUT", "/api/language", {"language": "es"}) == (200, {"language": "es"})
    server.restart()
    assert server.call("GET", "/api/language") == (200, {"language": "es"})
    status, body = server.call("PUT", "/api/language", {"language": "fr"})
    assert status == 422 and body["error"]["field"] == "language"
    assert server.call("GET", "/api/language") == (200, {"language": "es"})


def test_each_calendar_returns_its_sources_and_the_date_checked(server):
    status, body = server.call("GET", "/api/calendars")
    assert status == 200
    by_id = {c["id"]: c for c in body["calendars"]}
    assert set(by_id) == {"mx", "us"}
    assert [s["key"] for s in by_id["mx"]["sources"]] == ["LFT", "CPEUM", "LGIPE"]
    assert [s["key"] for s in by_id["us"]["sources"]] == ["USC", "EO"]
    for calendar in by_id.values():
        assert calendar["checked"] == "2026-10-26"
        assert all(s["url"].startswith("https://") and s["retrieved"] == "2026-10-26" for s in calendar["sources"])
