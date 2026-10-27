"""Fixtures that run the real server and a real browser."""

import os
import socket
import subprocess
import sys
import time
import urllib.error
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
def start_server():
    """Start uvicorn on a free port with the given SQLite file; return its URL. Every server stops at teardown."""
    procs = []

    def start(db: Path) -> str:
        port = free_port()
        env = {**os.environ, "DBD_DB_PATH": str(db)}
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
            cwd=ROOT,
            env=env,
        )
        procs.append(proc)
        url = f"http://127.0.0.1:{port}"
        for _ in range(100):
            try:
                urllib.request.urlopen(f"{url}/api/status", timeout=1)
                return url
            except urllib.error.HTTPError:
                return url  # the server answered, with an error status
            except OSError:
                time.sleep(0.1)
        raise RuntimeError("the server did not start")

    yield start
    for proc in procs:
        proc.terminate()
        proc.wait(timeout=10)


@pytest.fixture
def server(tmp_path, start_server):
    """A running server with its own SQLite file; yield its URL and file."""
    db = tmp_path / "app.db"
    yield {"url": start_server(db), "db": db}


@pytest.fixture
def page():
    """A Chromium page; CHROMIUM_PATH points to a browser already installed, if set."""
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        yield browser.new_page()
        browser.close()
