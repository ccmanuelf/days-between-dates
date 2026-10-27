"""The orphan check (plan step 7, SPEC AC10): every control on the page reaches a route that executes, every route of
the app has a caller, and every table is written and read.

It starts the server on a scratch database, drives every control of the page in a real browser and records each
request the page makes. FastAPI's own documentation routes (/docs, /docs/oauth2-redirect, /redoc, /openapi.json) are
the framework's, not the app's, and are left out by name. Tables are read from the SQL in app/storage.py.

    python scripts/orphans.py        # prints one orphan per line; exits 1 if there is any

CHROMIUM_PATH, if set, points to a Chromium already installed.
"""

import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent.parent
FRAMEWORK_ROUTES = {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}


def app_routes() -> list[tuple[str, str, re.Pattern]]:
    """(method, path, regex) for every route the app defines."""
    sys.path.insert(0, str(ROOT))
    from fastapi.routing import APIRoute

    from app.main import app

    return [
        (method, route.path, route.path_regex)
        for route in app.routes
        if isinstance(route, APIRoute) and route.path not in FRAMEWORK_ROUTES
        for method in sorted(route.methods)
    ]


def route_orphans(routes, requests) -> list[str]:
    """Routes no recorded request reached. `requests` holds (method, path, status) as the browser saw them."""
    orphans = []
    for method, path, regex in routes:
        if not any(m == method and regex.match(p) and s not in (404, 405) for m, p, s in requests):
            orphans.append(f"route without a caller: {method} {path}")
    return orphans


def table_orphans(sql: str) -> list[str]:
    """Tables created in `sql` that no statement writes, or none reads."""
    tables = re.findall(r"CREATE TABLE IF NOT EXISTS (\w+)", sql)
    written = set(re.findall(r"INSERT(?: OR \w+)? INTO (\w+)", sql)) | set(re.findall(r"UPDATE (\w+) SET", sql))
    read = set(re.findall(r"SELECT [^\"]*? FROM (\w+)", sql))
    orphans = [f"table never written: {t}" for t in tables if t not in written]
    orphans += [f"table never read: {t}" for t in tables if t not in read]
    return orphans


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def drive_page(url: str) -> tuple[list, list[str]]:
    """Use every control once; return the requests seen and the orphan controls."""
    from playwright.sync_api import sync_playwright

    requests, orphans = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        page = browser.new_context(locale="en-US").new_page()
        page.on("request", lambda r: requests.append(r))
        page.goto(url)
        page.wait_for_selector("body[data-ready=true]")

        def sent(method: str, path: str) -> list:
            return [r for r in requests if r.method == method and urlsplit(r.url).path == path]

        page.fill("#start", "2026-10-26")
        page.fill("#end", "2026-10-30")
        with page.expect_response(lambda r: "/api/count" in r.url):
            page.click("#count")
        query = parse_qs(urlsplit(sent("GET", "/api/count")[-1].url).query)
        for control, field, value in (("#start", "start", "2026-10-26"), ("#end", "end", "2026-10-30")):
            if query.get(field) != [value]:
                orphans.append(f"control does not reach its route: {control}")
        with page.expect_response(lambda r: "/api/count" in r.url):
            page.select_option("#calendar", "us")
        if parse_qs(urlsplit(sent("GET", "/api/count")[-1].url).query).get("calendar") != ["us"]:
            orphans.append("control does not reach its route: #calendar")

        page.fill("#new-day", "2026-10-28")
        with page.expect_response(lambda r: "/api/count" in r.url):
            page.click("#add")
        posts = sent("POST", "/api/holidays")
        if not posts or json.loads(posts[-1].post_data or "{}").get("day") != "2026-10-28":
            orphans.append("control does not reach its route: #new-day, #add")
        with page.expect_response(lambda r: "/api/count" in r.url):
            page.click("#own-list button.remove")
        if not sent("DELETE", "/api/holidays/us/2026-10-28"):
            orphans.append("control does not reach its route: .remove")

        with page.expect_response(lambda r: "/api/language" in r.url and r.request.method == "PUT"):
            page.select_option("#language", "es")
        puts = sent("PUT", "/api/language")
        if not puts or json.loads(puts[-1].post_data or "{}").get("language") != "es":
            orphans.append("control does not reach its route: #language")

        driven = {"language", "start", "end", "calendar", "count", "new-day", "add"}
        for control in page.locator("input, select, button").evaluate_all(
            "els => els.map(e => e.id || e.className)"
        ):
            if control not in driven and control != "remove":
                orphans.append(f"control not driven by this check: {control}")

        seen = []
        for r in requests:
            response = r.response()
            seen.append((r.method, urlsplit(r.url).path, response.status if response else 0))
        browser.close()
    return seen, orphans


def find_orphans() -> list[str]:
    with tempfile.TemporaryDirectory() as scratch:
        port = free_port()
        env = {k: v for k, v in os.environ.items() if k != "DBD_LIVE_DEMO"}
        env["DBD_DB_PATH"] = str(Path(scratch) / "app.db")
        server = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
            cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        url = f"http://127.0.0.1:{port}"
        try:
            for _ in range(100):
                try:
                    urllib.request.urlopen(f"{url}/api/config", timeout=1)
                    break
                except (urllib.error.URLError, OSError):
                    time.sleep(0.1)
            seen, orphans = drive_page(url)
        finally:
            server.terminate()
            server.wait(timeout=10)
    orphans += route_orphans(app_routes(), seen)
    orphans += table_orphans((ROOT / "app/storage.py").read_text())
    return orphans


if __name__ == "__main__":
    found = find_orphans()
    for orphan in found:
        print(orphan)
    print(f"{len(found)} orphan(s)")
    sys.exit(1 if found else 0)
