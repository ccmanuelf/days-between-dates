"""The scenarios through the page, on the running server: page → API → SQLite → back (plan step 6). These are the
tests that count for the SPEC's scenarios and for AC1–AC9, AC11, AC13 and AC14."""

import json
import re
import sqlite3
from pathlib import Path

import pytest
from playwright.sync_api import expect

from app.holidays import CALENDARS

ROOT = Path(__file__).resolve().parent.parent
STRINGS = json.loads((ROOT / "app/static/strings.json").read_text())
EN, ES = STRINGS["en"], STRINGS["es"]
CELLS = ["#total-snc", "#total-bc", "#business-snc", "#business-bc"]
TOTALS, BUSINESS = CELLS[:2], CELLS[2:]


def settle(page, action) -> None:
    """Do something on the page, then wait until the page has handled every answer it asked for (PAGE_PROBE in
    tests/conftest.py). An answer that has only arrived does not count."""
    before = page.evaluate("window.__started")
    action()
    page.wait_for_function(f"window.__started > {before} && window.__settled === window.__started")


def count(page, start: str, end: str):
    page.fill("#start", start)
    page.fill("#end", end)
    settle(page, lambda: page.click("#count"))


def choose_calendar(page, calendar: str):
    """Switch calendar: the page loads that calendar's list, and recounts with a result on screen."""
    settle(page, lambda: page.select_option("#calendar", calendar))


def choose_language(page, language: str):
    settle(page, lambda: page.select_option("#language", language))


def add_holiday(page, day: str):
    """Add a day of one's own: once it is stored, the page reloads its list, and recounts with a result on screen."""
    page.fill("#new-day", day)
    settle(page, lambda: page.click("#add"))


def remove_holiday(page, day: str):
    settle(page, lambda: page.click(f"#own-list li[data-day='{day}'] button.remove"))


def is_count(response) -> bool:
    return "/api/count" in response.url


def settled(page) -> int:
    return page.evaluate("window.__settled")


def expect_counts(page, values: tuple, cells: list = CELLS):
    for cell, value in zip(cells, values, strict=True):
        expect(page.locator(cell)).to_have_text(value)


def expect_own_list(page, days: list):
    """The days of one's own on screen, in order."""
    items = page.locator("#own-list li span")
    if days:
        expect(items).to_have_text(days)
    else:
        expect(items).to_have_count(0)


def test_s1_count_a_range_with_both_conventions_and_the_calendar_named(server, open_page):
    page = open_page(server.url)
    count(page, "2026-10-26", "2026-10-30")
    expect_counts(page, ("4", "5", "4", "5"))  # K1
    expect(page.locator("#active-calendar")).to_have_text(EN["active_calendar"].replace("{name}", "Mexico"))
    expect(page.locator("#result thead th")).to_have_text(["", EN["col_start_not_counted"], EN["col_both_counted"]])


def test_s2_the_same_date_twice(server, open_page):
    page = open_page(server.url)
    count(page, "2026-10-26", "2026-10-26")
    expect_counts(page, ("0", "1"), TOTALS)  # K2


def test_s3_reversed_dates_are_swapped_with_a_notice(server, open_page):
    page = open_page(server.url)
    count(page, "2026-10-30", "2026-10-26")
    expect_counts(page, ("4", "5", "4", "5"))  # K4, as K1
    expect(page.locator("#notice-swapped")).to_have_text(EN["notice_swapped"])
    expect(page.locator("#range")).to_have_text("From 2026-10-26 to 2026-10-30")
    count(page, "2026-10-26", "2026-10-30")
    expect(page.locator("#notice-swapped")).to_be_hidden()


def test_s4_switching_calendar_recomputes_and_names_it(server, open_page):
    page = open_page(server.url)
    count(page, "2026-11-09", "2026-11-13")  # Wednesday 11 November: Veterans Day in the US calendar only
    expect_counts(page, ("4", "5"), BUSINESS)
    choose_calendar(page, "us")
    expect_counts(page, ("3", "4"), BUSINESS)
    expect(page.locator("#active-calendar")).to_have_text("Calendar: United States")


def test_s5_an_own_holiday_is_stored_counted_and_listed_after_a_restart(server, open_page):
    page = open_page(server.url)
    choose_calendar(page, "us")
    count(page, "2026-10-26", "2026-10-30")
    expect_counts(page, ("4", "5"), BUSINESS)
    add_holiday(page, "2026-10-28")
    expect_own_list(page, ["2026-10-28"])
    expect_counts(page, ("3", "4"), BUSINESS)
    server.restart()
    page = open_page(server.url)
    choose_calendar(page, "us")
    expect_own_list(page, ["2026-10-28"])
    count(page, "2026-10-26", "2026-10-30")
    expect_counts(page, ("3", "4"), BUSINESS)


def test_s6_a_holiday_stays_in_its_calendar(server, open_page):
    page = open_page(server.url)
    choose_calendar(page, "us")
    add_holiday(page, "2026-10-28")
    expect_own_list(page, ["2026-10-28"])  # it is in the US list first
    choose_calendar(page, "mx")
    expect_own_list(page, [])
    expect(page.locator("#own-empty")).to_be_visible()
    count(page, "2026-10-26", "2026-10-30")
    expect_counts(page, ("4", "5"), BUSINESS)


def test_f1_a_late_list_does_not_replace_the_list_of_the_calendar_chosen_after_it(server, open_page):
    assert server.call("POST", "/api/holidays", {"calendar": "us", "day": "2026-10-28"})[0] == 201
    page = open_page(server.url)
    page.evaluate("window.__hold = 'holidays?calendar=us'")
    page.select_option("#calendar", "us")
    page.wait_for_function("window.__release !== null")  # the US list has arrived and is held
    before = settled(page)
    page.select_option("#calendar", "mx")
    page.wait_for_function(f"window.__settled >= {before + 1}")  # Mexico's list, handled
    page.evaluate("window.__release()")
    page.wait_for_function("window.__settled === window.__started")  # the late US list, handled too
    expect(page.locator("#own-title")).to_have_text(EN["own_title"].replace("{name}", "Mexico"))
    expect_own_list(page, [])
    expect(page.locator("#own-empty")).to_be_visible()


def test_f1_a_late_count_does_not_replace_the_count_of_the_calendar_chosen_after_it(server, open_page):
    page = open_page(server.url)
    count(page, "2026-11-09", "2026-11-13")  # Wednesday 11 November: Veterans Day in the US calendar only
    page.evaluate("window.__hold = 'count?calendar=us'")
    page.select_option("#calendar", "us")
    page.wait_for_function("window.__release !== null")  # the US recount has arrived and is held
    before = settled(page)
    page.select_option("#calendar", "mx")
    page.wait_for_function(f"window.__settled >= {before + 2}")  # Mexico's list and recount, handled
    page.evaluate("window.__release()")
    page.wait_for_function("window.__settled === window.__started")  # the late US recount, handled too
    expect(page.locator("#active-calendar")).to_have_text(EN["active_calendar"].replace("{name}", "Mexico"))
    expect_counts(page, ("4", "5", "4", "5"))


def test_s7_a_removed_holiday_is_gone_and_the_counts_return(server, open_page):
    page = open_page(server.url)
    choose_calendar(page, "us")
    count(page, "2026-10-26", "2026-10-30")
    add_holiday(page, "2026-10-28")
    expect_counts(page, ("3", "4"), BUSINESS)
    with page.expect_response(is_count):  # the page recounts after the removal
        remove_holiday(page, "2026-10-28")
    expect_own_list(page, [])
    expect_counts(page, ("4", "5"), BUSINESS)
    server.restart()
    page = open_page(server.url)
    choose_calendar(page, "us")
    expect_own_list(page, [])
    expect(page.locator("#own-empty")).to_be_visible()  # shown only once a list has been read


# 2026-10-26 (Monday) to 2026-12-31 (Thursday) with the US calendar: 67 days, 49 of them Monday to Friday, three of
# those federal holidays under 5 U.S.C. § 6103(a) (Veterans Day 11 November, Thanksgiving 26 November, Christmas 25
# December), so 46 business days with both dates counted and 45 without the start, itself a business day.
US_AUTUMN = ("66", "67", "45", "46")


@pytest.mark.parametrize("day", ["2026-10-31", "2026-11-01", "2026-12-25"])  # Saturday, Sunday, built-in holiday
def test_s8_a_day_is_excluded_once(server, open_page, day):
    page = open_page(server.url)
    choose_calendar(page, "us")
    count(page, "2026-10-26", "2026-12-31")
    expect_counts(page, US_AUTUMN)
    with page.expect_response(is_count):  # the page recounts after the add
        add_holiday(page, day)
    expect_own_list(page, [day])
    expect_counts(page, US_AUTUMN)  # the recount's own value: the day is excluded once


def test_s9_the_past_years_notice_in_both_cases(server, open_page):
    page = open_page(server.url)
    count(page, "2000-01-03", "2026-10-30")
    expect(page.locator("#notice-past-years")).to_have_text(EN["notice_past_years"])
    count(page, "9999-01-04", "9999-01-08")
    expect(page.locator("#notice-past-years")).to_be_hidden()


def test_s10_switching_to_spanish_changes_the_text_not_the_counts_and_survives_a_restart(server, open_page):
    page = open_page(server.url)
    count(page, "2026-01-01", "2026-12-31")
    expect_counts(page, ("364", "365", "254", "254"))  # K7, Mexico
    choose_language(page, "es")
    expect(page.locator("#result tbody th").nth(1)).to_have_text("Días hábiles")
    expect(page.locator("#note-business-days")).to_have_text(ES["note_business_days"])
    assert "715" in ES["note_business_days"]
    expect_counts(page, ("364", "365", "254", "254"))
    expect(page.locator("h1")).to_have_text(ES["title"])
    server.restart()
    page = open_page(server.url)  # a browser set to English: the stored choice wins
    expect(page.locator("html")).to_have_attribute("lang", "es")
    expect(page.locator("h1")).to_have_text(ES["title"])


def test_s11_the_note_on_local_election_days_with_mexico_only(server, open_page):
    page = open_page(server.url)
    count(page, "2026-10-26", "2026-10-30")
    expect(page.locator("#note-local-elections")).to_have_text(EN["note_local_elections"])
    choose_calendar(page, "us")
    expect(page.locator("#note-local-elections")).to_be_hidden()


@pytest.mark.parametrize("locale,strings", [("en-US", EN), ("es-MX", ES)], ids=["en", "es"])
def test_s12_the_storage_notice_on_the_live_demo_only(tmp_path, start_server, open_page, locale, strings):
    demo = start_server(tmp_path / "demo.db", env={"DBD_LIVE_DEMO": "1"})
    page = open_page(demo.url, locale)
    expect(page.locator("#demo-notice")).to_have_text(strings["notice_live_demo"])
    local = start_server(tmp_path / "local.db")
    page = open_page(local.url, locale)
    expect(page.locator("#demo-notice")).to_be_hidden()


def test_e1_an_invalid_date_is_refused_naming_the_field_and_nothing_is_stored(server, open_page):
    page = open_page(server.url)
    count(page, "2026-10-26", "2026-10-30")
    expect(page.locator("#result")).to_be_visible()
    count(page, "", "2026-10-30")
    expect(page.locator("#error")).to_have_text(EN["error_required"].replace("{field}", EN["field_start"]))
    expect(page.locator("#result")).to_be_hidden()  # no count beside the refusal
    count(page, "2026-02-30", "2026-10-30")
    expect(page.locator("#error")).to_have_text(EN["error_invalid_date"].replace("{field}", EN["field_start"]))
    count(page, "2026-10-26", "10000-01-01")
    expect(page.locator("#error")).to_have_text(EN["error_invalid_date"].replace("{field}", EN["field_end"]))
    add_holiday(page, "2026-02-30")
    expect(page.locator("#error")).to_have_text(EN["error_invalid_date"].replace("{field}", EN["field_day"]))
    with sqlite3.connect(server.db) as conn:  # the database itself, read after the refusals
        assert conn.execute("SELECT COUNT(*) FROM own_holidays").fetchone() == (0,)


def test_e2_a_duplicate_is_refused_and_the_list_is_unchanged(server, open_page):
    page = open_page(server.url)
    add_holiday(page, "2026-10-28")
    add_holiday(page, "2026-10-28")
    expect(page.locator("#error")).to_have_text(EN["error_duplicate"].replace("{field}", EN["field_day"]))
    expect_own_list(page, ["2026-10-28"])


def test_e3_an_unreadable_database_shows_no_count_and_keeps_the_language_on_screen(tmp_path, start_server, open_page):
    db = tmp_path / "app.db"
    db.write_bytes(b"this is not a database" * 100)
    page = open_page(start_server(db).url)
    with page.expect_response(is_count) as answer:
        count(page, "2026-10-26", "2026-10-30")
    assert answer.value.status == 503  # the count was asked, and refused
    expect(page.locator("#error")).to_have_text(EN["error_storage"])
    expect(page.locator("#result")).to_be_hidden()
    choose_language(page, "es")
    expect(page.locator("#error")).to_have_text(ES["error_language_not_stored"])
    expect(page.locator("h1")).to_have_text(ES["title"])  # the reading of "keeps the language on screen" in use


def test_e3_an_unwritable_database_refuses_the_holiday_and_still_counts(server, open_page):
    page = open_page(server.url)
    lock = sqlite3.connect(server.db, isolation_level=None)
    lock.execute("BEGIN IMMEDIATE")  # another writer holds the database
    try:
        add_holiday(page, "2026-10-28")
        expect(page.locator("#error")).to_have_text(EN["error_storage"])
        count(page, "2026-10-26", "2026-10-30")
        expect_counts(page, ("4", "5", "4", "5"))
    finally:
        lock.execute("ROLLBACK")
        lock.close()


def break_storage(db: Path, failure: str):
    """Make the database unwritable (another writer holds it) or unreadable (not a database); return the undo."""
    if failure == "unwritable":
        lock = sqlite3.connect(db, isolation_level=None)
        lock.execute("BEGIN IMMEDIATE")
        return lambda: (lock.execute("ROLLBACK"), lock.close())
    db.write_bytes(b"this is not a database" * 100)
    return lambda: None


@pytest.mark.parametrize("failure", ["unwritable", "unreadable"])
@pytest.mark.parametrize("edit", ["add", "remove"])
def test_e3_a_storage_failure_on_an_edit_takes_the_count_off_the_screen(server, open_page, edit, failure):
    page = open_page(server.url)
    choose_calendar(page, "us")
    count(page, "2026-10-26", "2026-10-30")
    if edit == "remove":
        add_holiday(page, "2026-10-28")
    expect(page.locator("#result")).to_be_visible()
    undo = break_storage(server.db, failure)
    try:
        if edit == "add":
            add_holiday(page, "2026-10-29")
        else:
            remove_holiday(page, "2026-10-28")
        expect(page.locator("#error")).to_have_text(EN["error_storage"])
        expect(page.locator("#result")).to_be_hidden()
    finally:
        undo()


def test_e3_an_unwritable_database_refuses_the_language_and_the_page_keeps_it_on_screen(server, open_page):
    page = open_page(server.url)
    undo = break_storage(server.db, "unwritable")
    try:
        choose_language(page, "es")
        expect(page.locator("#error")).to_have_text(ES["error_language_not_stored"])
        expect(page.locator("html")).to_have_attribute("lang", "es")
        expect(page.locator("h1")).to_have_text(ES["title"])
    finally:
        undo()
    with sqlite3.connect(server.db) as conn:  # the database itself: nothing was stored
        assert conn.execute("SELECT COUNT(*) FROM settings").fetchone() == (0,)


def test_n7_two_quick_language_choices_are_stored_in_the_order_made(server, open_page):
    page = open_page(server.url)
    page.evaluate("window.__holdRequest = 'PUT /api/language'")
    page.select_option("#language", "es")
    page.wait_for_function("window.__releaseRequest !== null")  # the Spanish choice is held before it is sent
    page.select_option("#language", "en")
    page.wait_for_function("window.__settled === window.__started - 1")  # all handled but the held choice
    page.evaluate("window.__releaseRequest()")
    page.wait_for_function("window.__settled === window.__started")
    expect(page.locator("html")).to_have_attribute("lang", "en")
    assert server.call("GET", "/api/language") == (200, {"language": "en"})  # the last choice made is the one kept


def test_n7_the_message_comes_from_the_latest_language_choice(server, open_page):
    page = open_page(server.url)
    undo = break_storage(server.db, "unwritable")
    page.evaluate("window.__hold = 'PUT /api/language'")
    page.select_option("#language", "es")
    page.wait_for_function("window.__release !== null")  # the Spanish choice was refused; its answer is held
    undo()
    page.select_option("#language", "en")
    page.wait_for_function("window.__settled === window.__started - 1")  # all handled but the held answer
    page.evaluate("window.__release()")
    page.wait_for_function("window.__settled === window.__started")
    expect(page.locator("#error")).to_be_hidden()  # the English choice was stored, and the page says nothing else
    assert server.call("GET", "/api/language") == (200, {"language": "en"})


def test_n7_a_choice_overtaken_before_its_turn_is_not_sent(server, open_page):
    page = open_page(server.url)
    sent = []
    page.on("request", lambda r: sent.append(json.loads(r.post_data)["language"]) if r.method == "PUT" else None)
    page.evaluate("window.__holdRequest = 'PUT /api/language'")
    page.select_option("#language", "es")
    page.wait_for_function("window.__releaseRequest !== null")  # the first Spanish choice is held before it is sent
    page.select_option("#language", "en")
    page.select_option("#language", "es")
    page.evaluate("window.__releaseRequest()")
    page.wait_for_function("window.__settled === window.__started")
    assert sent == ["es", "es"]  # English, overtaken before its turn, was never sent
    assert server.call("GET", "/api/language") == (200, {"language": "es"})


def test_n7_an_answer_overtaken_by_a_later_choice_sets_no_message(server, open_page):
    page = open_page(server.url)
    undo = break_storage(server.db, "unwritable")
    page.evaluate("window.__hold = 'PUT /api/language'")
    page.select_option("#language", "es")
    page.wait_for_function("window.__release !== null")  # the Spanish choice was refused; its answer is held
    undo()
    page.select_option("#language", "en")
    page.evaluate("window.__holdRequest = 'PUT /api/language'")
    page.evaluate("window.__release()")
    page.wait_for_function("window.__releaseRequest !== null")  # Spanish's answer handled; English's request held
    expect(page.locator("#error")).to_be_hidden()  # the refusal is not shown: a later choice was made
    page.evaluate("window.__releaseRequest()")
    page.wait_for_function("window.__settled === window.__started")
    expect(page.locator("#error")).to_be_hidden()


@pytest.mark.parametrize("calendar,business", [("mx", ("254", "254")), ("us", ("250", "250"))])
def test_k7_one_business_day_count_per_calendar_on_the_page(server, open_page, calendar, business):
    page = open_page(server.url)
    choose_calendar(page, calendar)
    count(page, "2026-01-01", "2026-12-31")
    expect_counts(page, ("364", "365") + business)


def test_ac11_each_calendar_shows_its_sources_and_the_date_checked(server, open_page):
    page = open_page(server.url)
    for calendar, links in (("mx", 3), ("us", 2)):
        block = page.locator(f".calendar-sources[data-calendar={calendar}]")
        expect(block.locator(".checked")).to_have_text(EN["checked"].replace("{date}", "2026-10-26"))
        expect(block.locator("a")).to_have_count(links)
        assert all(href.startswith("https://") for href in block.locator("a").evaluate_all("a => a.map(x => x.href)"))


# Each source as the page shows it (Q21): the official title verbatim, in its own language, as the link; around it the
# app's own words, in the page's language; names, designations and citations as published.
SOURCE_LINES = {
    "en": {
        "mx": [
            "Ley Federal del Trabajo, current text, last amended DOF 14-05-2026, art. 74 (retrieved 2026-10-26)",
            "Constitución Política de los Estados Unidos Mexicanos, last amended DOF 07-10-2026, art. 83 and the "
            "decree of DOF 10-02-2014, fifteenth transitional article (retrieved 2026-10-26)",
            "Ley General de Instituciones y Procedimientos Electorales, last amended DOF 02-06-2026, arts. 22.1, "
            "494.2 (retrieved 2026-10-26)",
        ],
        "us": [
            "5 U.S.C. § 6103, United States Code, 2024 Edition, GovInfo (U.S. Government Publishing Office) "
            "(retrieved 2026-10-26)",
            "Executive Order 11582, Observance of Holidays by Government Agencies, 11 February 1971, Federal Register "
            "vol. 36, no. 31, p. 2957 (retrieved 2026-10-26)",
        ],
    },
    "es": {
        "mx": [
            "Ley Federal del Trabajo, texto vigente, última reforma DOF 14-05-2026, art. 74 "
            "(consultado el 2026-10-26)",
            "Constitución Política de los Estados Unidos Mexicanos, última reforma DOF 07-10-2026, art. 83 y el "
            "decreto del DOF 10-02-2014, artículo décimo quinto transitorio (consultado el 2026-10-26)",
            "Ley General de Instituciones y Procedimientos Electorales, última reforma DOF 02-06-2026, arts. 22.1, "
            "494.2 (consultado el 2026-10-26)",
        ],
        "us": [
            "5 U.S.C. § 6103, United States Code, 2024 Edition, GovInfo (U.S. Government Publishing Office) "
            "(consultado el 2026-10-26)",
            "Executive Order 11582, Observance of Holidays by Government Agencies, 11 de febrero de 1971, Federal "
            "Register vol. 36, núm. 31, p. 2957 (consultado el 2026-10-26)",
        ],
    },
}
OFFICIAL_TITLES = {
    "mx": [
        ("Ley Federal del Trabajo", "https://www.diputados.gob.mx/LeyesBiblio/pdf/LFT.pdf"),
        ("Constitución Política de los Estados Unidos Mexicanos",
         "https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf"),
        ("Ley General de Instituciones y Procedimientos Electorales",
         "https://www.diputados.gob.mx/LeyesBiblio/pdf/LGIPE.pdf"),
    ],
    "us": [
        ("United States Code, 2024 Edition", "https://www.govinfo.gov/content/pkg/USCODE-2024-title5/html/"
         "USCODE-2024-title5-partIII-subpartE-chap61-subchapI-sec6103.htm"),
        ("Observance of Holidays by Government Agencies",
         "https://www.govinfo.gov/content/pkg/FR-1971-02-13/pdf/FR-1971-02-13.pdf"),
    ],
}


@pytest.mark.parametrize("locale,language", [("en-US", "en"), ("es-MX", "es")], ids=["en", "es"])
def test_ac13_the_sources_in_each_language_with_the_official_titles_verbatim(server, open_page, locale, language):
    page = open_page(server.url, locale)
    for calendar in ("mx", "us"):
        items = page.locator(f".calendar-sources[data-calendar={calendar}] li")
        expect(items).to_have_text(SOURCE_LINES[language][calendar])
        links = items.locator("a")
        expect(links).to_have_text([title for title, _ in OFFICIAL_TITLES[calendar]])
        for n, (_, url) in enumerate(OFFICIAL_TITLES[calendar]):
            expect(links.nth(n)).to_have_attribute("href", url)


@pytest.mark.parametrize("locale,expected", [("en-US", "en"), ("es-MX", "es"), ("fr-FR", "en")])
def test_q16_the_opening_language_follows_the_browser_when_none_is_stored(server, open_page, locale, expected):
    page = open_page(server.url, locale)
    expect(page.locator("html")).to_have_attribute("lang", expected)
    expect(page.locator("h1")).to_have_text(STRINGS[expected]["title"])


def test_q16_an_unreadable_stored_language_counts_as_none(server, open_page):
    with sqlite3.connect(server.db) as conn:
        conn.execute("INSERT INTO settings (key, value) VALUES ('language', 'xx')")
    page = open_page(server.url, "es-MX")
    expect(page.locator("html")).to_have_attribute("lang", "es")


def test_the_notices_in_spanish(server, open_page):
    page = open_page(server.url, "es-MX")
    count(page, "2026-10-30", "2000-01-03")
    expect(page.locator("#notice-swapped")).to_have_text(ES["notice_swapped"])
    expect(page.locator("#notice-past-years")).to_have_text(ES["notice_past_years"])
    expect(page.locator("#note-local-elections")).to_have_text(ES["note_local_elections"])
    expect(page.locator("#active-calendar")).to_have_text("Calendario: México")


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
    sources = {f"source_{s.key.lower()}" for rules in CALENDARS.values() for s in rules.SOURCES}
    used |= sources
    assert used <= set(EN), used - set(EN)
    assert all(STRINGS[lang][key].count("{title}") == 1 for lang in ("en", "es") for key in sources)


def test_the_page_sets_no_timers():
    """PAGE_PROBE (tests/conftest.py) counts an answer as handled on a timer, which holds while the page's own script
    sets none: a timer of the page's could run after the count, and these tests would read the page too early."""
    js = (ROOT / "app/static/app.js").read_text()
    assert not re.findall(r"\b(?:setTimeout|setInterval|requestAnimationFrame|requestIdleCallback)\b", js)
