"""The worked examples of the page's Help and "How this is calculated" (SPEC, S15, S16, AC18).

Each example is a range from the SPEC's known-answer checks, counted by the app's own code each time it is asked
for, with no holidays of the user's own, as the known answers assume. tests/test_guide.py checks each example's
total and business days, and its dates, against the known answer it names, and the business example's subtraction.
"""

from datetime import date

from app import counting
from app.days import Pair

# role on the page, known answer (SPEC, Known-answer checks), calendar, start and end as the user would enter them
EXAMPLES = (
    ("total", "K1", "mx", date(2026, 10, 26), date(2026, 10, 30)),
    ("business", "K9a", "us", date(2026, 6, 29), date(2026, 7, 6)),
    ("reversed", "K4", "mx", date(2026, 10, 30), date(2026, 10, 26)),
)


def as_pair(p: Pair) -> dict:
    return {"start_not_counted": p.start_not_counted, "both_counted": p.both_counted}


def examples() -> list[dict]:
    found = []
    for role, known, calendar, start, end in EXAMPLES:
        result = counting.count(calendar, start, end, own_holidays=[])
        found.append({
            "role": role,
            "known_answer": known,
            "calendar": calendar,
            "entered": {"start": start.isoformat(), "end": end.isoformat()},
            "start": result.days.start.isoformat(),
            "end": result.days.end.isoformat(),
            "swapped": result.days.swapped,
            "total": as_pair(result.days.total),
            "monday_to_friday": as_pair(result.days.monday_to_friday),
            "excluded": [d.isoformat() for d in result.excluded],
            "business": as_pair(result.business),
        })
    return found
