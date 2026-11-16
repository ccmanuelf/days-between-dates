"""Calendar arithmetic the calendar modules share. The Gregorian calendar and arithmetic need no source (SPEC)."""

from dataclasses import dataclass
from datetime import date

MONDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = 0, 3, 4, 5, 6


def weekday(ordinal: int) -> int:
    """Monday is 0. 0001-01-01, ordinal 1, was a Monday."""
    return (ordinal - 1) % 7


def is_monday_to_friday(ordinal: int) -> bool:
    return weekday(ordinal) < SATURDAY


def first_ordinal(year: int, month: int) -> int:
    """The ordinal of the first day of a month."""
    return date(year, month, 1).toordinal()


def nth_weekday(year: int, month: int, day_of_week: int, n: int) -> int:
    """The ordinal of the n-th given weekday of a month (n = 1 for the first)."""
    first = first_ordinal(year, month)
    return first + (day_of_week - weekday(first)) % 7 + 7 * (n - 1)


def last_weekday(year: int, month: int, day_of_week: int) -> int:
    """The ordinal of the last given weekday of a month."""
    next_first = first_ordinal(year + 1, 1) if month == 12 else first_ordinal(year, month + 1)
    last = next_first - 1
    return last - (weekday(last) - day_of_week) % 7


def year_of(ordinal: int) -> int:
    return date.fromordinal(ordinal).year


@dataclass(frozen=True)
class Source:
    key: str
    title: str
    url: str
    retrieved: str


@dataclass(frozen=True)
class Holiday:
    ordinal: int  # the day it is kept: for the United States, the observed day
    rule: str  # the rule it comes from, e.g. "lft-74-I"
