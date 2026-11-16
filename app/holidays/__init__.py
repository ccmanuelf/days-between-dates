"""The built-in calendars, one module per calendar.

Each module holds its rules, the sources they come from and the date they were checked, and answers one question:
which of its holidays fall on a Monday–Friday day between two day ordinals (1 = 0001-01-01), for the years the app
accepts, 1950 to 2150 (SPEC, Expectations), and the year after.
"""

from app.holidays import mexico, united_states

CALENDARS = {"mx": mexico, "us": united_states}
