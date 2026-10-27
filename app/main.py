"""The app: one page, served with the JSON API it calls."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app import storage

STATIC = Path(__file__).parent / "static"


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


@app.get("/")
def page() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/api/status")
def status():
    """Read from SQLite on every call, so the page shows what storage holds."""
    try:
        return {"storage": "ok", "schema_version": storage.schema_version()}
    except storage.StorageError as error:
        return JSONResponse(status_code=503, content={"storage": "error", "message": str(error)})
