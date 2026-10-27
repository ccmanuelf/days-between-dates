"""Mexico: the mandatory rest days of the federal labour law, Ley Federal del Trabajo, art. 74.

I 1 January · II first Monday of February · III third Monday of March · IV 1 May · V 16 September · VI third Monday
of November · VII 1 October every six years, when the federal executive power is transferred · VIII 25 December ·
IX the days the federal and local electoral laws set for ordinary elections.

VII: the term begins on 1 October and lasts six years (CPEUM art. 83), and the 2018–2024 term ended on
30 September 2024 (CPEUM, decree of DOF 10-02-2014, fifteenth transitional article): the transfer years are
2024 + 6n, applied to every year (SPEC, Q7).
IX: federal and judicial ordinary elections fall on the first Sunday of June (LGIPE arts. 22.1, 494.2), so they never
fall on a Monday–Friday day and change no count; they are not listed. A state's local election day is not built in:
the user's own list holds it (SPEC, Q13).
A rest day on a Saturday or Sunday is not moved: no article of the law moves one (SPEC, K8c).
"""

from datetime import date

from app.holidays.common import MONDAY, Holiday, Source, first_ordinal, is_monday_to_friday, nth_weekday, year_of

CHECKED = "2026-10-26"
SOURCES = (
    Source(
        "LFT",
        "Ley Federal del Trabajo",
        "https://www.diputados.gob.mx/LeyesBiblio/pdf/LFT.pdf",
        "2026-10-26",
    ),
    Source(
        "CPEUM",
        "Constitución Política de los Estados Unidos Mexicanos",
        "https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf",
        "2026-10-26",
    ),
    Source(
        "LGIPE",
        "Ley General de Instituciones y Procedimientos Electorales",
        "https://www.diputados.gob.mx/LeyesBiblio/pdf/LGIPE.pdf",
        "2026-10-26",
    ),
)


def _transfer_year(year: int) -> bool:
    return (year - 2024) % 6 == 0


def rest_days(year: int) -> list[Holiday]:
    """Every rest day of fractions I–VIII in a year, on whatever day of the week it falls."""
    days = [
        Holiday(date(year, 1, 1).toordinal(), "lft-74-I"),
        Holiday(nth_weekday(year, 2, MONDAY, 1), "lft-74-II"),
        Holiday(nth_weekday(year, 3, MONDAY, 3), "lft-74-III"),
        Holiday(date(year, 5, 1).toordinal(), "lft-74-IV"),
        Holiday(date(year, 9, 16).toordinal(), "lft-74-V"),
        Holiday(nth_weekday(year, 11, MONDAY, 3), "lft-74-VI"),
        Holiday(date(year, 12, 25).toordinal(), "lft-74-VIII"),
    ]
    if _transfer_year(year):
        days.append(Holiday(first_ordinal(year, 10), "lft-74-VII"))
    return sorted(days, key=lambda h: h.ordinal)


def weekday_holidays(first: int, last: int) -> list[Holiday]:
    """The rest days on a Monday–Friday day from ordinal `first` to `last`, both included."""
    if last < first:
        return []
    found = []
    for year in range(year_of(first), year_of(last) + 1):
        found += [h for h in rest_days(year) if first <= h.ordinal <= last and is_monday_to_friday(h.ordinal)]
    return found
