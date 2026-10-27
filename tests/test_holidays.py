"""Unit tests of the holiday rules (plan step 3). They do not count toward done: the known answers count through the
API and the page, once steps 5 and 6 wire these modules in. Expected values are the SPEC's known-answer checks."""

from datetime import date

import pytest

from app.holidays import CALENDARS, mexico, united_states
from app.holidays.common import MAX_ORDINAL, weekday

D = date.fromisoformat


def o(iso: str) -> int:
    return D(iso).toordinal()


def days(holidays) -> list[str]:
    return [date.fromordinal(h.ordinal).isoformat() for h in holidays]


def test_k8a_mexico_2026_rest_days_on_weekdays():
    found = mexico.weekday_holidays(o("2026-01-01"), o("2026-12-31"))
    assert days(found) == [
        "2026-01-01", "2026-02-02", "2026-03-16", "2026-05-01", "2026-09-16", "2026-11-16", "2026-12-25",
    ]
    assert [D(d).weekday() for d in days(found)] == [3, 0, 0, 4, 2, 0, 4]  # Thu, Mon, Mon, Fri, Wed, Mon, Fri
    assert "lft-74-VII" not in {h.rule for h in mexico.rest_days(2026)}  # 2026 is no transfer year


@pytest.mark.parametrize(
    "calendar,start_not_counted,both_counted",
    [(mexico, 6, 7), (united_states, 10, 11)],
    ids=["mexico", "united-states"],
)
def test_k7_holidays_on_weekdays_in_2026(calendar, start_not_counted, both_counted):
    # K7: Monday–Friday days 260 · 261; business days Mexico 254 · 254, United States 250 · 250.
    assert len(calendar.weekday_holidays(o("2026-01-02"), o("2026-12-31"))) == start_not_counted
    assert len(calendar.weekday_holidays(o("2026-01-01"), o("2026-12-31"))) == both_counted
    assert 260 - start_not_counted == 261 - both_counted == (254 if calendar is mexico else 250)


def test_k8b_mexico_transfer_day_2030():
    # 2030-09-30 (Mon) → 2030-10-04 (Fri): Tuesday 1 October 2030 is a rest day (art. 74 VII).
    assert days(mexico.weekday_holidays(o("2030-10-01"), o("2030-10-04"))) == ["2030-10-01"]
    assert days(mexico.weekday_holidays(o("2030-09-30"), o("2030-10-04"))) == ["2030-10-01"]
    assert {h.rule for h in mexico.rest_days(2024)} >= {"lft-74-VII"}
    assert "lft-74-VII" not in {h.rule for h in mexico.rest_days(2027)}


def test_k8c_mexico_a_weekend_rest_day_is_not_moved():
    # 2027-04-30 (Fri) → 2027-05-03 (Mon): 1 May 2027 is a Saturday and is not moved.
    may_first = [h for h in mexico.rest_days(2027) if h.rule == "lft-74-IV"][0]
    assert date.fromordinal(may_first.ordinal) == D("2027-05-01") and weekday(may_first.ordinal) == 5
    assert mexico.weekday_holidays(o("2027-04-30"), o("2027-05-03")) == []


@pytest.mark.parametrize(
    "kid,first,last,expected",
    [
        ("K9a", "2026-06-30", "2026-07-06", ["2026-07-03"]),  # Saturday 4 July 2026 kept on Friday 3 July
        ("K9b", "2027-07-03", "2027-07-06", ["2027-07-05"]),  # Sunday 4 July 2027 kept on Monday 5 July
        ("K9c", "2027-12-28", "2027-12-31", ["2027-12-31"]),  # New Year's Day 2028, a Saturday, kept in 2027
        ("K9d", "2033-06-18", "2033-06-21", ["2033-06-20"]),  # Juneteenth, Sunday 19 June 2033, kept on Monday
        ("K11", "9999-12-28", "9999-12-31", ["9999-12-31"]),  # New Year's Day of year 10000, a Saturday
    ],
)
def test_k9_k11_united_states_observed_days(kid, first, last, expected):
    assert days(united_states.weekday_holidays(o(first), o(last))) == expected


def test_k11_christmas_9999_is_kept_on_friday_24_december_outside_the_range():
    assert days(united_states.weekday_holidays(o("9999-12-24"), o("9999-12-24"))) == ["9999-12-24"]
    assert weekday(MAX_ORDINAL + 1) == 5  # 1 January 10000: a Saturday, as 1 January 2000 (400-year cycle)


def test_the_first_and_last_ranges_accepted():
    assert days(united_states.weekday_holidays(o("0001-01-01"), o("0001-01-01"))) == ["0001-01-01"]
    assert mexico.weekday_holidays(MAX_ORDINAL + 1, MAX_ORDINAL) == []  # an empty span after the last date


def test_united_states_2026_observed_days():
    found = united_states.weekday_holidays(o("2026-01-01"), o("2026-12-31"))
    assert days(found) == [
        "2026-01-01", "2026-01-19", "2026-02-16", "2026-05-25", "2026-06-19", "2026-07-03",
        "2026-09-07", "2026-10-12", "2026-11-11", "2026-11-26", "2026-12-25",
    ]


@pytest.mark.parametrize("key", sorted(CALENDARS))
def test_each_calendar_names_its_sources_and_the_date_checked(key):
    calendar = CALENDARS[key]
    assert calendar.CHECKED == "2026-10-26"
    assert calendar.SOURCES
    for source in calendar.SOURCES:
        assert source.url.startswith("https://") and source.retrieved == "2026-10-26"
