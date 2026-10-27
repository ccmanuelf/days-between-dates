"""United States: the federal legal public holidays, 5 U.S.C. § 6103(a), with their observed days.

New Year's Day, 1 January · Birthday of Martin Luther King, Jr., third Monday in January · Washington's Birthday,
third Monday in February · Memorial Day, last Monday in May · Juneteenth National Independence Day, 19 June ·
Independence Day, 4 July · Labor Day, first Monday in September · Columbus Day, second Monday in October · Veterans
Day, 11 November · Thanksgiving Day, fourth Thursday in November · Christmas Day, 25 December.

A holiday on a Saturday is kept on the Friday before (§ 6103(b)(1)); one on a Sunday, on the Monday after
(Executive Order 11582, sec. 3(a), for a Monday–Friday week), so New Year's Day on a Saturday is kept on
31 December of the year before (SPEC, K9c), and that of year 10000 on Friday 31 December 9999 (K11). Inauguration
Day, § 6103(c), is left out (SPEC, Q11).
"""

from app.holidays.common import (
    MAX_ORDINAL,
    MONDAY,
    SATURDAY,
    SUNDAY,
    THURSDAY,
    Holiday,
    Source,
    first_ordinal,
    is_monday_to_friday,
    last_weekday,
    nth_weekday,
    weekday,
    year_of,
)

CHECKED = "2026-10-26"
SOURCES = (
    Source(
        "USC",
        "5 U.S.C. § 6103, United States Code, 2024 Edition, GovInfo (U.S. Government Publishing Office)",
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title5/html/"
        "USCODE-2024-title5-partIII-subpartE-chap61-subchapI-sec6103.htm",
        "2026-10-26",
    ),
    Source(
        "EO",
        "Executive Order 11582, Observance of Holidays by Government Agencies, 11 February 1971, Federal Register "
        "vol. 36, no. 31, p. 2957",
        "https://www.govinfo.gov/content/pkg/FR-1971-02-13/pdf/FR-1971-02-13.pdf",
        "2026-10-26",
    ),
)


def _fixed(year: int, month: int, day: int) -> int:
    return first_ordinal(year, month) + day - 1


def calendar_days(year: int) -> list[Holiday]:
    """The eleven holidays of a year on their calendar days. For year 10000, only New Year's Day."""
    if year == 10000:
        return [Holiday(MAX_ORDINAL + 1, "new-years-day")]
    return [
        Holiday(_fixed(year, 1, 1), "new-years-day"),
        Holiday(nth_weekday(year, 1, MONDAY, 3), "birthday-of-martin-luther-king-jr"),
        Holiday(nth_weekday(year, 2, MONDAY, 3), "washingtons-birthday"),
        Holiday(last_weekday(year, 5, MONDAY), "memorial-day"),
        Holiday(_fixed(year, 6, 19), "juneteenth-national-independence-day"),
        Holiday(_fixed(year, 7, 4), "independence-day"),
        Holiday(nth_weekday(year, 9, MONDAY, 1), "labor-day"),
        Holiday(nth_weekday(year, 10, MONDAY, 2), "columbus-day"),
        Holiday(_fixed(year, 11, 11), "veterans-day"),
        Holiday(nth_weekday(year, 11, THURSDAY, 4), "thanksgiving-day"),
        Holiday(_fixed(year, 12, 25), "christmas-day"),
    ]


def observed(holiday: Holiday) -> Holiday:
    """Saturday → the Friday before; Sunday → the Monday after."""
    day = weekday(holiday.ordinal)
    if day == SATURDAY:
        return Holiday(holiday.ordinal - 1, holiday.rule)
    if day == SUNDAY:
        return Holiday(holiday.ordinal + 1, holiday.rule)
    return holiday


def observed_days(year: int) -> list[Holiday]:
    return [observed(h) for h in calendar_days(year)]


def weekday_holidays(first: int, last: int) -> list[Holiday]:
    """The observed holidays from ordinal `first` to `last`, both included; observed days are always Monday–Friday.

    The year after the range is read too: its New Year's Day, on a Saturday, is kept on the range's last day of the
    year."""
    if last < first:
        return []
    found = []
    for year in range(year_of(first), year_of(last) + 2):
        found += [h for h in observed_days(year) if first <= h.ordinal <= last]
    assert all(is_monday_to_friday(h.ordinal) for h in found)
    return sorted(found, key=lambda h: h.ordinal)
