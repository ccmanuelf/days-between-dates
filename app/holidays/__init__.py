"""The built-in calendars, one module per calendar.

Each module holds its rules, the sources they come from and the date they were checked, and answers one question:
which of its holidays fall on a Monday–Friday day between two day ordinals (1 = 0001-01-01). Ordinals let a range
that ends on 9999-12-31 reach a holiday observed for a date the date type cannot hold (SPEC, K11).
"""

from app.holidays import mexico, united_states

CALENDARS = {"mx": mexico, "us": united_states}
