"""The app: one page, served with the JSON API it calls.

Errors come back as {"error": {"code": ..., "field": ..., "message": ...}}: the page shows them in the user's language
from the code, and the field names where the input was refused (SPEC, E1). A storage failure is 503 with a fixed
message, never a count (SPEC, E3), and never the database's own error text. A request addressed to an unknown host
name gets TrustedHostMiddleware's plain-text 400; the page, served from an allowed host, does not receive it.
"""

import json
import os
import re
from contextlib import asynccontextmanager
from datetime import MAXYEAR, MINYEAR, date
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app import counting, guide, storage
from app.guide import as_pair as pair
from app.holidays import CALENDARS

STATIC = Path(__file__).parent / "static"
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
FIRST_YEAR, LAST_YEAR = 1950, 2150  # the years accepted: the owner's decision of 2026-11-15 (SPEC, Expectations)
STORAGE_MESSAGE = "The database cannot be read or written."
MAX_BODY = 4096  # bytes; a body the page sends with a valid date or language is under 100
# The host names a request may be addressed to: this machine, and any a deploy adds in DBD_ALLOWED_HOSTS (comma
# separated). A page on another site that points its own host name at this machine is refused (DNS rebinding).
ALLOWED_HOSTS = ["127.0.0.1", "localhost"] + [
    host.strip() for host in os.environ.get("DBD_ALLOWED_HOSTS", "").split(",") if host.strip()
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    # A database that cannot be read or written must not stop the server: each route reports it (SPEC, E3).
    try:
        storage.init()
    except storage.StorageError:
        pass
    yield


# No /docs, /redoc or /openapi.json: nothing on the page calls them (no orphans).
app = FastAPI(title="Days between dates", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)
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


def parse_date(field: str, value: object, years: tuple[int, int] = (FIRST_YEAR, LAST_YEAR)) -> date:
    """A date written YYYY-MM-DD, in the years FIRST_YEAR to LAST_YEAR unless `years` says otherwise. A JSON value that
    is not text, such as a number, is refused like any other invalid date."""
    first, last = years
    if value is None or value == "":
        raise Refused(422, "required", field, f"{field} is required.")
    try:
        if not isinstance(value, str) or not ISO_DATE.fullmatch(value):
            raise ValueError(value)
        day = date.fromisoformat(value)
        if not first <= day.year <= last:
            raise ValueError(value)
        return day
    except ValueError:
        raise Refused(422, "invalid_date", field, f"{field} is not a valid date (YYYY-MM-DD, years {first} to {last}).")


def parse_calendar(value: object) -> str:
    if not isinstance(value, str) or value not in CALENDARS:
        raise Refused(422, "unknown_calendar", "calendar", f"calendar must be one of: {', '.join(CALENDARS)}.")
    return value


async def json_body(request: Request) -> dict:
    """A JSON object sent as application/json, at most MAX_BODY bytes. Another content type is refused with 415: a
    page on another site can make the browser send a text/plain body without asking it first, but not an
    application/json one, so a write from another site does not reach the database. A larger body is refused with
    413 before more of it is read."""
    media_type = request.headers.get("content-type", "").split(";")[0].strip().lower()
    if media_type != "application/json":
        raise Refused(415, "invalid_body", None, "The request body must be sent as application/json.")
    declared = request.headers.get("content-length", "")
    too_large = Refused(413, "invalid_body", None, f"The request body is larger than {MAX_BODY} bytes.")
    if declared.isdigit() and int(declared) > MAX_BODY:
        raise too_large
    raw = bytearray()
    async for chunk in request.stream():
        raw += chunk
        if len(raw) > MAX_BODY:
            raise too_large
    try:
        body = json.loads(raw)
    except ValueError:
        body = None
    if not isinstance(body, dict):
        raise Refused(422, "invalid_body", None, "The request body must be a JSON object.")
    return body


@app.get("/")
def page() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/api/status")
def status() -> dict:
    """Read from SQLite on every call: the page checks it on load, and shows a storage failure before any count."""
    return {"storage": "ok", "schema_version": storage.schema_version()}


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


@app.get("/api/guide")
def guide_examples() -> dict:
    """The worked examples of Help and "How this is calculated", each a known answer counted now (SPEC, S16, AC18),
    and the first and last dates accepted, which Help names. The page asks for them each time one of those panels
    opens."""
    return {
        "examples": guide.examples(),
        "dates": {"first": date(FIRST_YEAR, 1, 1).isoformat(), "last": date(LAST_YEAR, 12, 31).isoformat()},
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
    when = parse_date("day", day, (MINYEAR, MAXYEAR))  # a day stored before the years were narrowed can still go
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
