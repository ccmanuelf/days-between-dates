"""A fixture for tests/guardians/test_every_write_reads_its_body_through_json_body.py: the patterns that guardian must
flag, written on purpose, each on its own line marked "guardian: flag". Nothing in this repository imports it
(searched for its file name), and pytest does not collect it: its name does not match `test_*.py`. The guardian reads
it as text; its main scan, of app/, does not read it."""

import fastapi  # guardian: flag
import pydantic  # guardian: flag
from fastapi import Body  # guardian: flag
from fastapi import FastAPI, Request
from fastapi import File  # guardian: flag
from fastapi import Form  # guardian: flag
from fastapi import UploadFile  # guardian: flag
from pydantic import BaseModel  # guardian: flag

app = FastAPI()


@app.post("/api/holidays")
async def add_holiday(request: Request) -> dict:
    return await request.json()  # guardian: flag


@app.put("/api/language")
async def set_language(request: Request) -> bytes:
    return await request.body()  # guardian: flag


@app.post("/api/form")
async def form(request: Request) -> dict:
    return dict(await request.form())  # guardian: flag


@app.post("/api/stream")
async def stream(request: Request) -> int:
    size = 0
    async for chunk in request.stream():  # guardian: flag
        size += len(chunk)
    return size
