"""The scenarios through the API on the running server (plan step 5). The page tests of step 6 are the ones that
count for the scenarios; these support them and pin each route's behaviour."""

import sqlite3

import pytest

from app.main import STORAGE_MESSAGE

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
    server.call("POST", "/api/holidays", {"calendar": "us", "day": "2026-10-28"})
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
    _, future = server.call("GET", "/api/count?calendar=mx&start=9999-01-04&end=9999-01-08")
    assert past["past_years"] is True and future["past_years"] is False


@pytest.mark.parametrize(
    "query,field,code",
    [
        ("calendar=mx&end=2026-10-30", "start", "required"),
        ("calendar=mx&start=&end=2026-10-30", "start", "required"),
        ("calendar=mx&start=2026-02-30&end=2026-10-30", "start", "invalid_date"),
        ("calendar=mx&start=2026-10-26&end=0000-01-01", "end", "invalid_date"),
        ("calendar=mx&start=2026-10-26&end=10000-01-01", "end", "invalid_date"),
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


@pytest.mark.parametrize("day", ["", "2026-02-30", "2026-13-01", "tomorrow"])
def test_e1_an_invalid_holiday_is_refused_and_nothing_is_stored(server, day):
    status, body = server.call("POST", "/api/holidays", {"calendar": "us", "day": day})
    assert status == 422 and body["error"]["field"] == "day"
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


def test_the_live_demo_setting_is_off_on_a_local_install(server):
    assert server.call("GET", "/api/config") == (200, {"live_demo": False})


def test_the_live_demo_setting_is_on_where_the_deploy_sets_it(tmp_path, start_server):
    demo = start_server(tmp_path / "app.db", env={"DBD_LIVE_DEMO": "1"})
    assert demo.call("GET", "/api/config") == (200, {"live_demo": True})
