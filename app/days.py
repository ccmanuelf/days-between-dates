"""Day counts between two dates, under both conventions.

The two conventions (SPEC, S1): "start not counted" counts the days after the start up to and including the end;
"both counted" also counts the start. Dates are handled as day ordinals (1 = 0001-01-01), so a range that ends on
9999-12-31 never needs a date after it, which the date type cannot hold.
"""

from dataclasses import dataclass
from datetime import date

# Monday is 0, as in date.weekday(). 0001-01-01 (ordinal 1) was a Monday.
SATURDAY = 5


def weekday_of_ordinal(ordinal: int) -> int:
    """The weekday of a day ordinal, also for ordinals past 9999-12-31."""
    return (ordinal - 1) % 7


def monday_to_friday(first: int, last: int) -> int:
    """Monday–Friday days from ordinal `first` to ordinal `last`, both included; 0 when `last` < `first`."""
    days = last - first + 1
    if days <= 0:
        return 0
    weeks, rest = divmod(days, 7)
    count = 5 * weeks
    tail = first + 7 * weeks
    count += sum(1 for o in range(tail, tail + rest) if weekday_of_ordinal(o) < SATURDAY)
    return count


@dataclass(frozen=True)
class Pair:
    """One value per convention."""

    start_not_counted: int
    both_counted: int


@dataclass(frozen=True)
class Span:
    """The ordinals a convention counts: `first` to `last`, both included (empty when `last` < `first`)."""

    first: int
    last: int


@dataclass(frozen=True)
class DayCounts:
    start: date
    end: date
    swapped: bool
    total: Pair
    monday_to_friday: Pair
    spans: tuple[Span, Span]  # start not counted, both counted


def count_days(start: date, end: date) -> DayCounts:
    """Count total days and Monday–Friday days; reversed dates are swapped and flagged (SPEC, S3)."""
    swapped = end < start
    if swapped:
        start, end = end, start
    s, e = start.toordinal(), end.toordinal()
    not_counted = Span(s + 1, e)
    counted = Span(s, e)
    return DayCounts(
        start=start,
        end=end,
        swapped=swapped,
        total=Pair(e - s, e - s + 1),
        monday_to_friday=Pair(
            monday_to_friday(not_counted.first, not_counted.last),
            monday_to_friday(counted.first, counted.last),
        ),
        spans=(not_counted, counted),
    )
