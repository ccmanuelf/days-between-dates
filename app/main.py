"""The app: one page, served with the JSON API it calls."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import storage

STATIC = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    storage.init()
    yield


app = FastAPI(title="Days between dates", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def page() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/api/status")
def status() -> dict:
    """Read from SQLite on every call, so the page shows what storage holds."""
    return {"storage": "ok", "schema_version": storage.schema_version()}
