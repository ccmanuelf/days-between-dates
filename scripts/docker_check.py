"""The Docker check: the app running from compose.yaml answers through the real wiring, and keeps its data in the
volume. CI runs it in the `docker` job (.github/workflows/ci.yml), with compose's default project on a runner that
is discarded after the job.

By hand, the steps name their own compose project, `dbd-check`, so they store their test holiday in the volume
`dbd-check_app-data` and delete that volume at the end, not `days-between-dates_app-data`, where `docker compose up`
keeps your own holidays. The app answers on BACKEND_PORT (default 8765, `.env.example`); with that port taken, set
BACKEND_PORT on each `up` and use that port in the address.

    docker compose -p dbd-check up --build -d
    python scripts/docker_check.py serves http://127.0.0.1:8765     # page, assets, a known answer, adds a holiday
    docker compose -p dbd-check down && docker compose -p dbd-check up -d
    python scripts/docker_check.py kept http://127.0.0.1:8765       # the holiday came back from the volume
    docker compose -p dbd-check down -v --rmi local

Its imports (__future__, json, re, sys, time, urllib) are from Python's standard library, so it needs no package install
on the machine that runs Docker. It imports under Python 3.9 and 3.12, and CI runs it under 3.13. Exits 1 on the
first failed check.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request

# Outside K1's range (2026-10-26 to 2026-10-30), so the K1 check here is unaffected. It is inside K7's range, so a
# later check that expects an empty database needs a fresh volume.
HOLIDAY = {"calendar": "mx", "day": "2026-12-24"}


def request(base: str, method: str, path: str, body: dict | None = None) -> tuple[int, str]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


def wait_until_up(base: str, seconds: int = 60) -> None:
    for _ in range(seconds):
        try:
            if request(base, "GET", "/api/status")[0] == 200:
                return
        except OSError:
            pass
        time.sleep(1)
    fail(f"/api/status did not answer 200 within {seconds} s")


def fail(message: str) -> None:
    print(f"FAIL  {message}")
    sys.exit(1)


def check(name: str, ok: bool, detail: str = "") -> None:
    if not ok:
        fail(f"{name}  {detail}")
    print(f"PASS  {name}")


def serves(base: str) -> None:
    status, html = request(base, "GET", "/")
    scripts = re.findall(r'<script[^>]+src="(/assets/[^"]+\.js)"', html)
    styles = re.findall(r'<link[^>]+href="(/assets/[^"]+\.css)"', html)
    check("page served", status == 200 and len(scripts) == 1 and len(styles) == 1, f"HTTP {status}")
    # The built page's script calls the API and carries both languages; its stylesheet carries the standard's tokens.
    assets = (("page script", scripts[0], ("/api/count", "Días entre fechas")),
              ("page stylesheet", styles[0], ("--primary", "--motion-scale")),
              ("page icon", "/favicon.svg", ("<svg",)))
    for name, asset, markers in assets:
        status, text = request(base, "GET", asset)
        check(f"{name} served", status == 200 and all(m in text for m in markers), f"HTTP {status}")
    # K1 (SPEC.md, Known-answer checks): 2026-10-26 to 2026-10-30, Mexico: total 4 · 5, business 4 · 5.
    status, text = request(base, "GET", "/api/count?calendar=mx&start=2026-10-26&end=2026-10-30")
    body = json.loads(text) if status == 200 else {}
    got = (body.get("total"), body.get("business"))
    want = ({"start_not_counted": 4, "both_counted": 5}, {"start_not_counted": 4, "both_counted": 5})
    check("K1 through the API", got == want, f"HTTP {status} {got}")
    status, text = request(base, "POST", "/api/holidays", HOLIDAY)
    check("own holiday stored", status == 201, f"HTTP {status} {text}")


def kept(base: str) -> None:
    status, text = request(base, "GET", "/api/holidays?calendar=mx")
    days = json.loads(text).get("holidays") if status == 200 else None
    check("own holiday kept in the volume", days == [HOLIDAY["day"]], f"HTTP {status} {days}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("serves", "kept"):
        sys.exit(__doc__)
    mode, base_url = sys.argv[1], sys.argv[2].rstrip("/")
    wait_until_up(base_url)
    if mode == "serves":
        serves(base_url)
    else:
        kept(base_url)
