"""The guide's worked examples through the API on the running server (SPEC, S16, AC18): every example is a known
answer, counted by the app's own code, with no holidays of the user's own except the one K10 names."""

from datetime import date

from test_known_answers import ROWS

# The known answers by (id, calendar): total and business days, each (start not counted, both counted). K4 is K1's
# range entered in reverse: swapped, with K1's counts. K10 is K3's range with one own holiday, Saturday 2026-10-31:
# business 1 · 2, unchanged (SPEC, Known-answer checks).
KNOWN = {(kid, calendar): (total, business) for kid, calendar, _, _, total, business in ROWS}
KNOWN[("K4", "mx")] = KNOWN[("K1", "mx")]
KNOWN[("K10", "mx")] = ((3, 4), (1, 2))
RANGES = {(kid, calendar): (start, end) for kid, calendar, start, end, _, _ in ROWS}
RANGES[("K4", "mx")] = ("2026-10-30", "2026-10-26")
RANGES[("K10", "mx")] = ("2026-10-30", "2026-11-02")
OWN = {"K10": ["2026-10-31"]}  # the only example with a day of one's own


def examples(server) -> list[dict]:
    status, body = server.call("GET", "/api/guide")
    assert status == 200, body
    return body["examples"]


def pair(value: dict) -> tuple[int, int]:
    return value["start_not_counted"], value["both_counted"]


def test_every_example_is_a_known_answer_with_its_counts(server):
    found = examples(server)
    assert {e["role"] for e in found} == {"total", "weekend", "business", "own", "reversed"}
    for example in found:
        key = (example["known_answer"], example["calendar"])
        assert key in KNOWN, f"{key} is not in the known-answer table"
        assert (example["entered"]["start"], example["entered"]["end"]) == RANGES[key]
        assert example["own_holidays"] == OWN.get(example["known_answer"], []), key
        total, business = KNOWN[key]
        assert pair(example["total"]) == total, key
        if business is not None:
            assert pair(example["business"]) == business, key


def test_the_reversed_example_is_swapped(server):
    (example,) = [e for e in examples(server) if e["role"] == "reversed"]
    assert example["swapped"] is True
    assert (example["start"], example["end"]) == ("2026-10-26", "2026-10-30")


def test_the_business_example_subtracts_the_days_it_names(server):
    """Monday–Friday days minus the excluded days give the business days: the arithmetic the page shows."""
    (example,) = [e for e in examples(server) if e["role"] == "business"]
    assert example["excluded"] == ["2026-07-03"]  # Independence Day 2026, Saturday, observed Friday 3 July (K9a)
    excluded = [date.fromisoformat(d) for d in example["excluded"]]
    assert all(d.weekday() < 5 and example["start"] <= d.isoformat() <= example["end"] for d in excluded)
    for convention in (0, 1):  # start not counted, both counted; the start, a Monday, is not excluded
        assert pair(example["monday_to_friday"])[convention] - len(excluded) == pair(example["business"])[convention]


def test_own_holidays_do_not_change_the_examples(server):
    """A day of one's own inside K1's range changes the count, not the worked example."""
    status, _ = server.call("POST", "/api/holidays", {"calendar": "mx", "day": "2026-10-28"})
    assert status == 201
    status, body = server.call("GET", "/api/count?calendar=mx&start=2026-10-26&end=2026-10-30")
    assert status == 200 and pair(body["business"]) == (3, 4)
    (example,) = [e for e in examples(server) if e["role"] == "total"]
    assert pair(example["business"]) == (4, 5)


def test_the_own_example_is_k10_a_saturday_that_changes_no_count(server):
    """K10: an own holiday on a Saturday leaves K3's business days as they were (SPEC, S8)."""
    by_role = {e["role"]: e for e in examples(server)}
    own, weekend = by_role["own"], by_role["weekend"]
    assert date.fromisoformat(own["own_holidays"][0]).weekday() == 5  # Saturday
    assert (own["known_answer"], weekend["known_answer"]) == ("K10", "K3")
    assert pair(own["business"]) == pair(weekend["business"]) == (1, 2)
    assert own["excluded"] == weekend["excluded"] == []


def test_the_guide_names_the_dates_accepted(server):
    """The first and last dates the app accepts, from its own limit (SPEC, Expectations), for the guide's text."""
    status, body = server.call("GET", "/api/guide")
    assert status == 200, body
    assert body["dates"] == {"first": "1950-01-01", "last": "2150-12-31"}
