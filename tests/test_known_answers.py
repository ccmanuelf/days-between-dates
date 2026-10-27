"""The SPEC's known-answer checks, K1–K11, through the API on the running server (plan steps 5 and 8): these count
for AC1 and AC2, and CI runs them on every pull request and every push to main. Each row is the SPEC's, with its
id."""

import pytest

# id, calendar, start, end, total (start not counted, both counted), business (same order; None where the SPEC
# states totals only)
ROWS = [
    ("K1", "mx", "2026-10-26", "2026-10-30", (4, 5), (4, 5)),
    ("K1", "us", "2026-10-26", "2026-10-30", (4, 5), (4, 5)),
    ("K2", "mx", "2026-10-26", "2026-10-26", (0, 1), None),
    ("K3", "mx", "2026-10-30", "2026-11-02", (3, 4), (1, 2)),
    ("K3", "us", "2026-10-30", "2026-11-02", (3, 4), (1, 2)),
    ("K5", "mx", "2028-02-28", "2028-03-01", (2, 3), None),
    ("K6", "mx", "2027-02-28", "2027-03-01", (1, 2), None),
    ("K7", "mx", "2026-01-01", "2026-12-31", (364, 365), (254, 254)),
    ("K7", "us", "2026-01-01", "2026-12-31", (364, 365), (250, 250)),
    ("K8b", "mx", "2030-09-30", "2030-10-04", (4, 5), (3, 4)),
    ("K8c", "mx", "2027-04-30", "2027-05-03", (3, 4), (1, 2)),
    ("K9a", "us", "2026-06-29", "2026-07-06", (7, 8), (4, 5)),
    ("K9b", "us", "2027-07-02", "2027-07-06", (4, 5), (1, 2)),
    ("K9c", "us", "2027-12-27", "2027-12-31", (4, 5), (3, 4)),
    ("K9d", "us", "2033-06-17", "2033-06-21", (4, 5), (1, 2)),
    ("K11", "us", "9999-12-27", "9999-12-31", (4, 5), (3, 4)),
]

# K8a: Mexico's 2026 rest days on weekdays, as one-day ranges: each is a Monday–Friday day that counts no business
# day.
K8A = ["2026-01-01", "2026-02-02", "2026-03-16", "2026-05-01", "2026-09-16", "2026-11-16", "2026-12-25"]


def counted(server, calendar, start, end):
    status, body = server.call("GET", f"/api/count?calendar={calendar}&start={start}&end={end}")
    assert status == 200, body
    return body


@pytest.mark.parametrize("kid,calendar,start,end,total,business", ROWS, ids=[f"{r[0]}-{r[1]}" for r in ROWS])
def test_known_answer(server, kid, calendar, start, end, total, business):
    body = counted(server, calendar, start, end)
    assert (body["total"]["start_not_counted"], body["total"]["both_counted"]) == total
    if business is not None:
        assert (body["business"]["start_not_counted"], body["business"]["both_counted"]) == business
    assert body["calendar"] == calendar and not body["swapped"]


def test_k4_reversed_dates_are_swapped_with_the_notice_flag(server):
    forward = counted(server, "mx", "2026-10-26", "2026-10-30")
    body = counted(server, "mx", "2026-10-30", "2026-10-26")
    assert body["swapped"] is True
    assert (body["start"], body["end"]) == ("2026-10-26", "2026-10-30")
    assert (body["total"], body["business"]) == (forward["total"], forward["business"])


@pytest.mark.parametrize("day", K8A)
def test_k8a_mexico_2026_rest_days(server, day):
    assert counted(server, "mx", day, day)["business"] == {"start_not_counted": 0, "both_counted": 0}


def test_k10_an_own_holiday_on_a_saturday_changes_nothing(server):
    assert server.call("POST", "/api/holidays", {"calendar": "mx", "day": "2026-10-31"})[0] == 201
    body = counted(server, "mx", "2026-10-30", "2026-11-02")
    assert (body["business"]["start_not_counted"], body["business"]["both_counted"]) == (1, 2)
