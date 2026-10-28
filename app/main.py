"""The app: one page, served with the JSON API it calls.

Errors come back as {"error": {"code": ..., "field": ..., "message": ...}}: the page shows them in the user's language
from the code, and the field names where the input was refused (SPEC, E1). A storage failure is 503 with a fixed
message, never a count (SPEC, E3), and never the database's own error text.
"""

import os
import re
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from app import counting, storage
from app.holidays import CALENDARS

STATIC = Path(__file__).parent / "static"
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
STORAGE_MESSAGE = "The database cannot be read or written."


@asynccontextmanager
async def lifespan(_: FastAPI):
    # A database that cannot be read or written must not stop the server: each route reports it (SPEC, E3).
    try:
        storage.init()
    except storage.StorageError:
        pass
    yield


app = FastAPI(title="Days between dates", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class Refused(Exception):
    def __init__(self, status: int, code: str, field: str | None, message: str):
        self.status, self.code, self.field, self.message = status, code, field, message


@app.exception_handler(Refused)
def refused(_: Request, error: Refused) -> JSONResponse:
    return JSONResponse(
        status_code=error.status,
        content={"error": {"code": error.code, "field": error.field, "message": error.message}},
    )


@app.exception_handler(storage.StorageError)
def storage_failed(_: Request, __: storage.StorageError) -> JSONResponse:
    return JSONResponse(
        status_code=503, content={"error": {"code": "storage", "field": None, "message": STORAGE_MESSAGE}}
    )


def parse_date(field: str, value: object) -> date:
    """A date written YYYY-MM-DD, years 1 to 9999: the range Python's date type holds. A JSON value that is not text,
    such as a number, is refused like any other invalid date."""
    if value is None or value == "":
        raise Refused(422, "required", field, f"{field} is required.")
    try:
        if not isinstance(value, str) or not ISO_DATE.fullmatch(value):
            raise ValueError(value)
        return date.fromisoformat(value)
    except ValueError:
        raise Refused(422, "invalid_date", field, f"{field} is not a valid date (YYYY-MM-DD, years 1 to 9999).")


def parse_calendar(value: object) -> str:
    if not isinstance(value, str) or value not in CALENDARS:
        raise Refused(422, "unknown_calendar", "calendar", f"calendar must be one of: {', '.join(CALENDARS)}.")
    return value


async def json_body(request: Request) -> dict:
    try:
        body = await request.json()
    except ValueError:
        body = None
    if not isinstance(body, dict):
        raise Refused(422, "invalid_body", None, "The request body must be a JSON object.")
    return body


def pair(p) -> dict:
    return {"start_not_counted": p.start_not_counted, "both_counted": p.both_counted}


@app.get("/")
def page() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/api/status")
def status() -> dict:
    """Read from SQLite on every call: the page checks it on load, and shows a storage failure before any count."""
    return {"storage": "ok", "schema_version": storage.schema_version()}


@app.get("/api/config")
def config() -> dict:
    """Whether this server runs as the live demo, whose storage resets on restart (SPEC, S12). Off unless the deploy
    sets DBD_LIVE_DEMO=1, so a local install never shows the notice."""
    return {"live_demo": os.environ.get("DBD_LIVE_DEMO") == "1"}


@app.get("/api/calendars")
def calendars() -> dict:
    """Each built-in calendar, its sources and the date its rules were checked (SPEC, AC11)."""
    return {
        "calendars": [
            {
                "id": key,
                "checked": rules.CHECKED,
                "sources": [
                    {"key": s.key, "title": s.title, "url": s.url, "retrieved": s.retrieved} for s in rules.SOURCES
                ],
            }
            for key, rules in CALENDARS.items()
        ]
    }


@app.get("/api/count")
def count(calendar: str | None = None, start: str | None = None, end: str | None = None) -> dict:
    cal = parse_calendar(calendar)
    first, last = parse_date("start", start), parse_date("end", end)
    result = counting.count(cal, first, last)
    return {
        "calendar": cal,
        "start": result.days.start.isoformat(),
        "end": result.days.end.isoformat(),
        "swapped": result.days.swapped,
        "past_years": result.past_years,
        "total": pair(result.days.total),
        "business": pair(result.business),
    }


@app.get("/api/holidays")
def list_holidays(calendar: str | None = None) -> dict:
    cal = parse_calendar(calendar)
    return {"calendar": cal, "holidays": [d.isoformat() for d in storage.list_holidays(cal)]}


@app.post("/api/holidays", status_code=201)
async def add_holiday(request: Request) -> dict:
    body = await json_body(request)
    cal = parse_calendar(body.get("calendar"))
    day = parse_date("day", body.get("day"))
    try:
        storage.add_holiday(cal, day)
    except storage.DuplicateHoliday:
        raise Refused(409, "duplicate", "day", f"{day.isoformat()} is already in the {cal} list.")
    return {"calendar": cal, "day": day.isoformat()}


@app.delete("/api/holidays/{calendar}/{day}", status_code=204)
def remove_holiday(calendar: str, day: str) -> Response:
    cal = parse_calendar(calendar)
    when = parse_date("day", day)
    if not storage.remove_holiday(cal, when):
        raise Refused(404, "not_found", "day", f"{when.isoformat()} is not in the {cal} list.")
    return Response(status_code=204)


@app.get("/api/language")
def get_language() -> dict:
    """The stored language, or null when none is stored or the stored one cannot be read (SPEC, Q16)."""
    return {"language": storage.get_language()}


@app.put("/api/language")
async def set_language(request: Request) -> dict:
    body = await json_body(request)
    language = body.get("language")
    if language not in storage.LANGUAGES:
        raise Refused(
            422, "unknown_language", "language", f"language must be one of: {', '.join(storage.LANGUAGES)}."
        )
    storage.set_language(language)
    return {"language": language}
