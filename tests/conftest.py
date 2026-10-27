"""Fixtures that run the real server and a real browser."""

import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def server(tmp_path):
    """Start uvicorn on a free port with its own SQLite file; yield its URL and file."""
    db = tmp_path / "app.db"
    port = free_port()
    env = {**os.environ, "DBD_DB_PATH": str(db)}
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT,
        env=env,
    )
    url = f"http://127.0.0.1:{port}"
    try:
        for _ in range(100):
            try:
                urllib.request.urlopen(f"{url}/api/status", timeout=1)
                break
            except OSError:
                time.sleep(0.1)
        else:
            raise RuntimeError("the server did not start")
        yield {"url": url, "db": db}
    finally:
        proc.terminate()
        proc.wait(timeout=10)


@pytest.fixture
def page():
    """A Chromium page; CHROMIUM_PATH points to a browser already installed, if set."""
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        yield browser.new_page()
        browser.close()
