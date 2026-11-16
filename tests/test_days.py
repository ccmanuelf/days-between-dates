"""Unit tests of the day counts (plan step 2). They do not count toward done: the known answers count through the
API and the page, once steps 5 and 6 wire this module in. Expected values are the SPEC's known-answer checks."""

from datetime import date, timedelta

import pytest

from app.days import count_days, monday_to_friday, weekday_of_ordinal

D = date.fromisoformat

# id, start, end, total (start not counted, both counted), Monday–Friday days (same order)
KNOWN = [
    ("K1", "2026-10-26", "2026-10-30", (4, 5), (4, 5)),
    ("K2", "2026-10-26", "2026-10-26", (0, 1), (0, 1)),
    ("K3", "2026-10-30", "2026-11-02", (3, 4), (1, 2)),
    ("K5", "2028-02-28", "2028-03-01", (2, 3), None),
    ("K6", "2027-02-28", "2027-03-01", (1, 2), None),
    ("K7", "2026-01-01", "2026-12-31", (364, 365), (260, 261)),
]


@pytest.mark.parametrize("kid,start,end,total,weekdays", KNOWN, ids=[k[0] for k in KNOWN])
def test_known_answers(kid, start, end, total, weekdays):
    c = count_days(D(start), D(end))
    assert not c.swapped
    assert (c.total.start_not_counted, c.total.both_counted) == total
    if weekdays is not None:
        assert (c.monday_to_friday.start_not_counted, c.monday_to_friday.both_counted) == weekdays


def test_k4_reversed_dates_are_swapped_and_flagged():
    forward = count_days(D("2026-10-26"), D("2026-10-30"))
    c = count_days(D("2026-10-30"), D("2026-10-26"))
    assert c.swapped
    assert (c.start, c.end) == (D("2026-10-26"), D("2026-10-30"))
    assert (c.total, c.monday_to_friday, c.spans) == (forward.total, forward.monday_to_friday, forward.spans)


def test_the_last_dates_accepted():
    c = count_days(D("2150-12-27"), D("2150-12-31"))  # Sunday to Thursday
    assert (c.total.start_not_counted, c.total.both_counted) == (4, 5)
    assert (c.monday_to_friday.start_not_counted, c.monday_to_friday.both_counted) == (4, 4)
    last = count_days(D("2150-12-31"), D("2150-12-31"))
    assert (last.total.start_not_counted, last.total.both_counted) == (0, 1)
    assert last.monday_to_friday.start_not_counted == 0


def test_the_first_dates_accepted():
    c = count_days(D("1950-01-01"), D("1950-01-07"))  # 1950-01-01 was a Sunday
    assert (c.total.start_not_counted, c.total.both_counted) == (6, 7)
    assert (c.monday_to_friday.start_not_counted, c.monday_to_friday.both_counted) == (5, 5)


def test_weekday_of_ordinal_matches_the_date_type():
    for d in (D("1950-01-01"), D("2000-01-01"), D("2026-10-26"), D("2150-12-31"), D("2151-01-01")):
        assert weekday_of_ordinal(d.toordinal()) == d.weekday()


def test_monday_to_friday_matches_a_day_by_day_count():
    base = D("2026-10-01")
    for length in range(0, 30):
        for offset in range(7):
            first = base + timedelta(days=offset)
            last = first + timedelta(days=length - 1)
            expected = sum(1 for i in range(length) if (first + timedelta(days=i)).weekday() < 5)
            assert monday_to_friday(first.toordinal(), last.toordinal()) == expected
