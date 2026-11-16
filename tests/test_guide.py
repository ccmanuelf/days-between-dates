"""The User Guide's worked examples, read from the guide's own text in each language and counted again on the running
server (SPEC, S16, AC18; the app template's User Guide rule): each example's dates and numbers are taken from the
sentence the page shows, run through the API the feature uses, and compared with the SPEC's known answers. Changing
the text or the code alone fails them."""

import re
from datetime import date, timedelta

import pytest

from app.days import monday_to_friday
from app.holidays import CALENDARS
from test_known_answers import ROWS
from test_page import STRINGS

KNOWN = {(kid, calendar): (total, business) for kid, calendar, _, _, total, business in ROWS}
RANGES = {(kid, calendar): (start, end) for kid, calendar, start, end, _, _ in ROWS}
WEEKDAYS = {
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "es": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
}
LANGUAGES = ["en", "es"]
ISO = re.compile(r"\d{4}-\d{2}-\d{2}")


def read(language: str, key: str) -> tuple[str | None, list[str], list[int]]:
    """The known answer an example names, its dates and its other numbers, in the order the sentence gives them."""
    text = STRINGS[language][key]
    named = re.search(r"\((K\d+[a-d]?)", text)
    kid = named.group(1) if named else None
    rest = ISO.sub(" ", text)
    if kid:
        rest = rest.replace(kid, " ")
    return kid, ISO.findall(text), [int(n) for n in re.findall(r"\b\d+\b", rest)]


def counted(server, calendar: str, start: str, end: str) -> dict:
    status, body = server.call("GET", f"/api/count?calendar={calendar}&start={start}&end={end}")
    assert status == 200, body
    return body


def pair(value: dict) -> tuple[int, int]:
    return value["start_not_counted"], value["both_counted"]


def named_weekday(language: str, day: str) -> str:
    return WEEKDAYS[language][date.fromisoformat(day).weekday()]


@pytest.mark.parametrize("language", LANGUAGES)
def test_the_dates_accepted_are_the_ones_the_app_accepts(server, language):
    _, (first, last), _ = read(language, "help_range_dates")
    before = (date.fromisoformat(first) - timedelta(days=1)).isoformat()
    after = (date.fromisoformat(last) + timedelta(days=1)).isoformat()
    assert counted(server, "mx", first, last)["start"] == first
    for outside in (before, after):
        status, body = server.call("GET", f"/api/count?calendar=mx&start={outside}&end={first}")
        assert status == 422 and body["error"]["code"] == "invalid_date", (outside, body)


@pytest.mark.parametrize("language", LANGUAGES)
def test_k1_the_total_example(server, language):
    kid, (start, end), numbers = read(language, "example_total")
    assert (kid, (start, end)) == ("K1", RANGES[("K1", "mx")])
    assert tuple(numbers) == pair(counted(server, "mx", start, end)["total"]) == KNOWN[("K1", "mx")][0]


@pytest.mark.parametrize("language", LANGUAGES)
def test_k3_the_weekend_example(server, language):
    kid, (start, end), numbers = read(language, "example_weekend")
    assert (kid, (start, end)) == ("K3", RANGES[("K3", "mx")])
    body = counted(server, "mx", start, end)
    total, business = KNOWN[("K3", "mx")]
    assert tuple(numbers) == pair(body["total"]) + pair(body["business"]) == total + business
    text = STRINGS[language]["example_weekend"]
    assert f"({named_weekday(language, start)})" in text and f"({named_weekday(language, end)})" in text


@pytest.mark.parametrize("language", LANGUAGES)
def test_k9a_the_business_days_example(server, language):
    """The Monday-to-Friday days, less the observed holiday the sentence names, give the business days."""
    kid, (start, end, holiday), numbers = read(language, "example_business")
    assert (kid, (start, end)) == ("K9a", RANGES[("K9a", "us")])
    first, last = date.fromisoformat(start).toordinal(), date.fromisoformat(end).toordinal()
    observed = [date.fromordinal(h.ordinal).isoformat() for h in CALENDARS["us"].weekday_holidays(first, last)]
    assert observed == [holiday]
    weekdays = (monday_to_friday(first + 1, last), monday_to_friday(first, last))
    business = pair(counted(server, "us", start, end)["business"])
    assert tuple(numbers) == weekdays + business
    assert business == KNOWN[("K9a", "us")][1] == (weekdays[0] - 1, weekdays[1] - 1)


@pytest.mark.parametrize("language", LANGUAGES)
def test_k10_the_own_holiday_example(server, language):
    """K10: one own holiday on a Saturday, in K3's range, leaves its business days as they were (SPEC, S8)."""
    kid, (own, start, end), numbers = read(language, "example_own")
    assert (kid, (start, end)) == ("K10", RANGES[("K3", "mx")])
    assert named_weekday(language, own) in STRINGS[language]["example_own"]
    assert server.call("POST", "/api/holidays", {"calendar": "mx", "day": own})[0] == 201
    try:
        assert tuple(numbers) == pair(counted(server, "mx", start, end)["business"]) == KNOWN[("K3", "mx")][1]
    finally:
        assert server.call("DELETE", f"/api/holidays/mx/{own}")[0] == 204


@pytest.mark.parametrize("language", LANGUAGES)
def test_k4_the_reversed_example(server, language):
    kid, (entered_start, entered_end, start, end), numbers = read(language, "example_reversed")
    assert (kid, numbers) == ("K4", [])
    assert (entered_start, entered_end) == ("2026-10-30", "2026-10-26")  # K1's range entered in reverse (SPEC, K4)
    body = counted(server, "mx", entered_start, entered_end)
    assert body["swapped"] is True and (body["start"], body["end"]) == (start, end) == RANGES[("K1", "mx")]


def test_every_example_in_the_guide_is_read_by_a_test():
    """A new example key needs its own test above: one this module does not read would be an untested claim."""
    examples = {key for key in STRINGS["en"] if key.startswith("example_")} | {"help_range_dates"}
    assert examples == {"example_total", "example_weekend", "example_business", "example_own", "example_reversed",
                        "help_range_dates"}
