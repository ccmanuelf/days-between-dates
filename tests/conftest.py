"""Fixtures that run the real server and a real browser."""

import json
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


class Server:
    """uvicorn on a free port with its own SQLite file. A restart stops the process and starts a new one on the same
    file, so what survives it was read back from storage."""

    def __init__(self, db: Path, env: dict | None = None):
        self.db, self.env, self.proc, self.url = db, env or {}, None, None
        self.start()

    def start(self) -> None:
        port = free_port()
        env = {k: v for k, v in os.environ.items() if k != "DBD_LIVE_DEMO"}  # a local install unless asked
        env.update({"DBD_DB_PATH": str(self.db), **self.env})
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
            cwd=ROOT,
            env=env,
        )
        self.url = f"http://127.0.0.1:{port}"
        for _ in range(100):
            try:
                urllib.request.urlopen(f"{self.url}/api/config", timeout=1)
                return
            except urllib.error.HTTPError:
                return  # the server answered, with an error status
            except OSError:
                time.sleep(0.1)
        raise RuntimeError("the server did not start")

    def stop(self) -> None:
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            self.proc.wait(timeout=10)

    def restart(self) -> None:
        self.stop()
        self.start()

    def call(self, method: str, path: str, body: dict | None = None) -> tuple[int, dict | None]:
        """One HTTP request to the running server; the status and the decoded JSON body (None when empty)."""
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(f"{self.url}{path}", data=data, method=method)
        if data is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw, status = response.read(), response.status
        except urllib.error.HTTPError as error:
            raw, status = error.read(), error.code
        return status, (json.loads(raw) if raw else None)


@pytest.fixture
def start_server():
    """Start servers on given SQLite files; every one stops at teardown."""
    servers = []

    def start(db: Path, env: dict | None = None) -> Server:
        server = Server(db, env)
        servers.append(server)
        return server

    yield start
    for server in servers:
        server.stop()


@pytest.fixture
def server(tmp_path, start_server) -> Server:
    """A running server, run as a local install, with its own SQLite file."""
    return start_server(tmp_path / "app.db")


@pytest.fixture
def browser():
    """Chromium; CHROMIUM_PATH points to a browser already installed, if set."""
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        yield browser
        browser.close()


@pytest.fixture
def open_page(browser):
    """Open the app's page at a URL, in a browser set to a language (navigator.language), once it is ready."""

    def open_(url: str, locale: str = "en-US"):
        page = browser.new_context(locale=locale).new_page()
        page.goto(url)
        page.wait_for_selector("body[data-ready=true]")
        return page

    return open_


@pytest.fixture
def page(browser):
    """A Chromium page in a browser set to English."""
    return browser.new_context(locale="en-US").new_page()
