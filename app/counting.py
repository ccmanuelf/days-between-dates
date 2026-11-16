"""Business days: the Monday–Friday days of a range, minus the active calendar's holidays and the user's own.

A day is excluded once, whether it is a built-in holiday, one of the user's own, or both; an own holiday on a
Saturday or Sunday excludes nothing (SPEC, S8). The user's own holidays are read from storage on every count, so a
storage failure raises and no count leaves them out (SPEC, E3).
"""

from dataclasses import dataclass
from datetime import date

from app import storage
from app.days import DayCounts, Pair, count_days, monday_to_friday
from app.holidays import CALENDARS
from app.holidays.common import is_monday_to_friday


@dataclass(frozen=True)
class Count:
    calendar: str
    days: DayCounts
    business: Pair
    past_years: bool
    excluded: tuple[date, ...]  # the Monday–Friday days the both-counted span leaves out, built-in and own


def count(
    calendar: str, start: date, end: date, today: date | None = None, own_holidays: list[date] | None = None
) -> Count:
    """`own_holidays`, when given, replaces the stored list: the guide's worked examples pass the days their known
    answer names, none except K10's one day (SPEC, S16)."""
    days = count_days(start, end)
    rules = CALENDARS[calendar]
    own_days = storage.list_holidays(calendar) if own_holidays is None else own_holidays
    own = [d.toordinal() for d in own_days]
    business, excluded = [], set()
    for span in days.spans:
        built_in = {h.ordinal for h in rules.weekday_holidays(span.first, span.last)}
        mine = {o for o in own if span.first <= o <= span.last and is_monday_to_friday(o)}
        excluded = built_in | mine  # the last span is the both-counted one
        business.append(monday_to_friday(span.first, span.last) - len(excluded))
    this_year = (today or date.today()).year
    return Count(
        calendar,
        days,
        Pair(*business),
        past_years=days.start.year < this_year,
        excluded=tuple(date.fromordinal(o) for o in sorted(excluded)),
    )
