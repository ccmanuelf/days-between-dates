"""The scenarios through the page, on the running server: page → API → SQLite → back (plan step 6). These are the
tests that count for the SPEC's scenarios and for AC1–AC9, AC11, AC13 and AC14."""

import json
import re
import sqlite3
from pathlib import Path

import pytest
from playwright.sync_api import expect

ROOT = Path(__file__).resolve().parent.parent
STRINGS = json.loads((ROOT / "app/static/strings.json").read_text())
EN, ES = STRINGS["en"], STRINGS["es"]
CELLS = ["#total-snc", "#total-bc", "#business-snc", "#business-bc"]


def is_count(response) -> bool:
    return "/api/count" in response.url


def count(page, start: str, end: str):
    page.fill("#start", start)
    page.fill("#end", end)
    with page.expect_response(is_count):
        page.click("#count")


def choose_calendar(page, calendar: str):
    """Switch calendar; with a result on screen the page recounts, and this waits for it."""
    if page.locator("#result").is_visible():
        with page.expect_response(is_count):
            page.select_option("#calendar", calendar)
    else:
        with page.expect_response(lambda r: "/api/holidays" in r.url):
            page.select_option("#calendar", calendar)


def add_holiday(page, day: str, recount: bool = True):
    page.fill("#new-day", day)
    if recount and page.locator("#result").is_visible():
        with page.expect_response(is_count):
            page.click("#add")
    else:
        with page.expect_response(lambda r: "/api/holidays" in r.url and r.request.method == "POST"):
            page.click("#add")


def cells(page) -> tuple:
    return tuple(page.locator(cell).inner_text() for cell in CELLS)


def own_list(page) -> list:
    return page.locator("#own-list li").evaluate_all("items => items.map(i => i.dataset.day)")


def test_s1_count_a_range_with_both_conventions_and_the_calendar_named(server, open_page):
    page = open_page(server.url)
    count(page, "2026-10-26", "2026-10-30")
    assert cells(page) == ("4", "5", "4", "5")  # K1
    assert page.locator("#active-calendar").inner_text() == EN["active_calendar"].replace("{name}", "Mexico")
    assert page.locator("#result thead th").all_inner_texts()[-2:] == [
        EN["col_start_not_counted"], EN["col_both_counted"],
    ]


def test_s2_the_same_date_twice(server, open_page):
    page = open_page(server.url)
    count(page, "2026-10-26", "2026-10-26")
    assert cells(page)[:2] == ("0", "1")  # K2


def test_s3_reversed_dates_are_swapped_with_a_notice(server, open_page):
    page = open_page(server.url)
    count(page, "2026-10-30", "2026-10-26")
    assert cells(page) == ("4", "5", "4", "5")  # K4, as K1
    assert page.locator("#notice-swapped").inner_text() == EN["notice_swapped"]
    assert page.locator("#range").inner_text() == "From 2026-10-26 to 2026-10-30"
    count(page, "2026-10-26", "2026-10-30")
    assert page.locator("#notice-swapped").is_hidden()


def test_s4_switching_calendar_recomputes_and_names_it(server, open_page):
    page = open_page(server.url)
    count(page, "2026-11-09", "2026-11-13")  # Wednesday 11 November: Veterans Day in the US calendar only
    assert cells(page)[2:] == ("4", "5")
    choose_calendar(page, "us")
    assert cells(page)[2:] == ("3", "4")
    assert page.locator("#active-calendar").inner_text() == "Calendar: United States"


def test_s5_an_own_holiday_is_stored_counted_and_listed_after_a_restart(server, open_page):
    page = open_page(server.url)
    choose_calendar(page, "us")
    count(page, "2026-10-26", "2026-10-30")
    assert cells(page)[2:] == ("4", "5")
    add_holiday(page, "2026-10-28")
    assert own_list(page) == ["2026-10-28"]
    assert cells(page)[2:] == ("3", "4")
    server.restart()
    page = open_page(server.url)
    choose_calendar(page, "us")
    assert own_list(page) == ["2026-10-28"]
    count(page, "2026-10-26", "2026-10-30")
    assert cells(page)[2:] == ("3", "4")


def test_s6_a_holiday_stays_in_its_calendar(server, open_page):
    page = open_page(server.url)
    choose_calendar(page, "us")
    add_holiday(page, "2026-10-28")
    choose_calendar(page, "mx")
    assert own_list(page) == []
    assert page.locator("#own-empty").is_visible()
    count(page, "2026-10-26", "2026-10-30")
    assert cells(page)[2:] == ("4", "5")


def test_s7_a_removed_holiday_is_gone_and_the_counts_return(server, open_page):
    page = open_page(server.url)
    choose_calendar(page, "us")
    count(page, "2026-10-26", "2026-10-30")
    add_holiday(page, "2026-10-28")
    assert cells(page)[2:] == ("3", "4")
    with page.expect_response(is_count):
        page.click("#own-list li[data-day='2026-10-28'] button.remove")
    assert own_list(page) == []
    assert cells(page)[2:] == ("4", "5")
    server.restart()
    page = open_page(server.url)
    choose_calendar(page, "us")
    assert own_list(page) == []


@pytest.mark.parametrize("day", ["2026-10-31", "2026-11-01", "2026-12-25"])  # Saturday, Sunday, built-in holiday
def test_s8_a_day_is_excluded_once(server, open_page, day):
    page = open_page(server.url)
    choose_calendar(page, "us")
    count(page, "2026-10-26", "2026-12-31")
    before = cells(page)
    add_holiday(page, day)
    assert own_list(page) == [day]
    assert cells(page) == before


def test_s9_the_past_years_notice_in_both_cases(server, open_page):
    page = open_page(server.url)
    count(page, "2000-01-03", "2026-10-30")
    assert page.locator("#notice-past-years").inner_text() == EN["notice_past_years"]
    count(page, "9999-01-04", "9999-01-08")
    assert page.locator("#notice-past-years").is_hidden()


def test_s10_switching_to_spanish_changes_the_text_not_the_counts_and_survives_a_restart(server, open_page):
    page = open_page(server.url)
    count(page, "2026-01-01", "2026-12-31")
    before = cells(page)
    with page.expect_response(lambda r: "/api/language" in r.url and r.request.method == "PUT"):
        page.select_option("#language", "es")
    assert page.locator("#result tbody th").nth(1).inner_text() == "Días hábiles"
    assert page.locator("#note-business-days").inner_text() == ES["note_business_days"]
    assert "715" in ES["note_business_days"]
    assert cells(page) == before
    assert page.locator("h1").inner_text() == ES["title"]
    server.restart()
    page = open_page(server.url)  # a browser set to English: the stored choice wins
    assert page.locator("html").get_attribute("lang") == "es"
    assert page.locator("h1").inner_text() == ES["title"]


def test_s11_the_note_on_local_election_days_with_mexico_only(server, open_page):
    page = open_page(server.url)
    count(page, "2026-10-26", "2026-10-30")
    assert page.locator("#note-local-elections").inner_text() == EN["note_local_elections"]
    choose_calendar(page, "us")
    assert page.locator("#note-local-elections").is_hidden()


@pytest.mark.parametrize("locale,strings", [("en-US", EN), ("es-MX", ES)], ids=["en", "es"])
def test_s12_the_storage_notice_on_the_live_demo_only(tmp_path, start_server, open_page, locale, strings):
    demo = start_server(tmp_path / "demo.db", env={"DBD_LIVE_DEMO": "1"})
    page = open_page(demo.url, locale)
    assert page.locator("#demo-notice").inner_text() == strings["notice_live_demo"]
    local = start_server(tmp_path / "local.db")
    page = open_page(local.url, locale)
    assert page.locator("#demo-notice").is_hidden()


def test_e1_an_invalid_date_is_refused_naming_the_field_and_nothing_is_stored(server, open_page):
    page = open_page(server.url)
    count(page, "", "2026-10-30")
    assert page.locator("#error").inner_text() == EN["error_required"].replace("{field}", EN["field_start"])
    assert page.locator("#result").is_hidden()
    count(page, "2026-02-30", "2026-10-30")
    assert page.locator("#error").inner_text() == EN["error_invalid_date"].replace("{field}", EN["field_start"])
    count(page, "2026-10-26", "10000-01-01")
    assert page.locator("#error").inner_text() == EN["error_invalid_date"].replace("{field}", EN["field_end"])
    add_holiday(page, "2026-02-30")
    assert page.locator("#error").inner_text() == EN["error_invalid_date"].replace("{field}", EN["field_day"])
    with sqlite3.connect(server.db) as conn:  # the database itself, read after the refusals
        assert conn.execute("SELECT COUNT(*) FROM own_holidays").fetchone() == (0,)


def test_e2_a_duplicate_is_refused_and_the_list_is_unchanged(server, open_page):
    page = open_page(server.url)
    add_holiday(page, "2026-10-28")
    add_holiday(page, "2026-10-28")
    assert page.locator("#error").inner_text() == EN["error_duplicate"].replace("{field}", EN["field_day"])
    assert own_list(page) == ["2026-10-28"]


def test_e3_an_unreadable_database_shows_no_count_and_keeps_the_language_on_screen(tmp_path, start_server, open_page):
    db = tmp_path / "app.db"
    db.write_bytes(b"this is not a database" * 100)
    page = open_page(start_server(db).url)
    count(page, "2026-10-26", "2026-10-30")
    assert page.locator("#error").inner_text() == EN["error_storage"]
    assert page.locator("#result").is_hidden()
    with page.expect_response(lambda r: "/api/language" in r.url and r.request.method == "PUT"):
        page.select_option("#language", "es")
    assert page.locator("#error").inner_text() == ES["error_language_not_stored"]
    assert page.locator("h1").inner_text() == ES["title"]  # the reading of "keeps the language on screen" in use


def test_e3_an_unwritable_database_refuses_the_holiday_and_still_counts(server, open_page):
    page = open_page(server.url)
    lock = sqlite3.connect(server.db, isolation_level=None)
    lock.execute("BEGIN IMMEDIATE")  # another writer holds the database
    try:
        add_holiday(page, "2026-10-28")
        assert page.locator("#error").inner_text() == EN["error_storage"]
        count(page, "2026-10-26", "2026-10-30")
        assert cells(page) == ("4", "5", "4", "5")
    finally:
        lock.execute("ROLLBACK")
        lock.close()


@pytest.mark.parametrize("calendar,business", [("mx", ("254", "254")), ("us", ("250", "250"))])
def test_k7_one_business_day_count_per_calendar_on_the_page(server, open_page, calendar, business):
    page = open_page(server.url)
    choose_calendar(page, calendar)
    count(page, "2026-01-01", "2026-12-31")
    assert cells(page) == ("364", "365") + business


def test_ac11_each_calendar_shows_its_sources_and_the_date_checked(server, open_page):
    page = open_page(server.url)
    for calendar, links in (("mx", 3), ("us", 2)):
        block = page.locator(f".calendar-sources[data-calendar={calendar}]")
        assert block.locator(".checked").inner_text() == EN["checked"].replace("{date}", "2026-10-26")
        assert block.locator("a").count() == links
        assert all(href.startswith("https://") for href in block.locator("a").evaluate_all("a => a.map(x => x.href)"))


@pytest.mark.parametrize("locale,expected", [("en-US", "en"), ("es-MX", "es"), ("fr-FR", "en")])
def test_q16_the_opening_language_follows_the_browser_when_none_is_stored(server, open_page, locale, expected):
    page = open_page(server.url, locale)
    assert page.locator("html").get_attribute("lang") == expected
    assert page.locator("h1").inner_text() == STRINGS[expected]["title"]


def test_q16_an_unreadable_stored_language_counts_as_none(server, open_page):
    with sqlite3.connect(server.db) as conn:
        conn.execute("INSERT INTO settings (key, value) VALUES ('language', 'xx')")
    page = open_page(server.url, "es-MX")
    assert page.locator("html").get_attribute("lang") == "es"


def test_the_notices_in_spanish(server, open_page):
    page = open_page(server.url, "es-MX")
    count(page, "2026-10-30", "2000-01-03")
    assert page.locator("#notice-swapped").inner_text() == ES["notice_swapped"]
    assert page.locator("#notice-past-years").inner_text() == ES["notice_past_years"]
    assert page.locator("#note-local-elections").inner_text() == ES["note_local_elections"]
    assert page.locator("#active-calendar").inner_text() == "Calendario: México"


def test_every_string_exists_in_both_languages():
    assert set(EN) == set(ES)
    assert all(value.strip() for value in list(EN.values()) + list(ES.values()))
    html = (ROOT / "app/static/index.html").read_text()
    js = (ROOT / "app/static/app.js").read_text()
    used = set(re.findall(r'data-i18n(?:-placeholder)?="(\w+)"', html)) | set(re.findall(r'\bt\("(\w+)"', js))
    used |= {f"calendar_{c}" for c in ("mx", "us")}
    used |= {f"error_{c}" for c in (
        "required", "invalid_date", "unknown_calendar", "unknown_language", "duplicate", "not_found",
        "invalid_body", "storage",
    )}
    used |= {f"field_{f}" for f in ("start", "end", "day", "calendar", "language")}
    assert used <= set(EN), used - set(EN)
