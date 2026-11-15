"""The security audit's fixes of 2026-11-15, on the running server: a write with a body (adding a holiday, storing the
language) must be sent as application/json, at most 4096 bytes; a request must be addressed to a known host name; and
environment files stay out of git."""

import http.client
import json
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

import pytest

ROOT = Path(__file__).resolve().parent.parent
ADD = {"calendar": "mx", "day": "2026-10-28"}


def send(server, method: str, path: str, body: bytes | None = None, headers: dict | None = None,
         chunked: bool = False) -> tuple[int, bytes]:
    """One request that sends no Content-Type unless one is given (urllib would add its own), and the answer's status
    and body."""
    address = urlsplit(server.url)
    conn = http.client.HTTPConnection(address.hostname, address.port, timeout=30)
    try:
        if chunked:
            conn.request(method, path, body=iter([body]), headers=headers or {}, encode_chunked=True)
        else:
            conn.request(method, path, body=body, headers=headers or {})
        answer = conn.getresponse()
        return answer.status, answer.read()
    finally:
        conn.close()


def stored_holidays(server) -> list[str]:
    status, body = server.call("GET", "/api/holidays?calendar=mx")
    assert status == 200, body
    return body["holidays"]


@pytest.mark.parametrize("content_type", [None, "text/plain", "text/plain;charset=UTF-8",
                                          "application/x-www-form-urlencoded", "multipart/form-data; boundary=x"])
def test_a_write_not_sent_as_json_is_refused_with_415_and_stores_nothing(server, content_type):
    headers = {"Content-Type": content_type} if content_type else {}
    status, body = send(server, "POST", "/api/holidays", json.dumps(ADD).encode(), headers)
    assert status == 415, body
    assert json.loads(body)["error"]["code"] == "invalid_body"
    status, _ = send(server, "PUT", "/api/language", json.dumps({"language": "es"}).encode(), headers)
    assert status == 415
    assert stored_holidays(server) == []
    assert server.call("GET", "/api/language")[1] == {"language": None}


def test_a_write_sent_as_json_with_a_charset_is_accepted(server):
    headers = {"Content-Type": "application/json; charset=utf-8"}
    status, body = send(server, "POST", "/api/holidays", json.dumps(ADD).encode(), headers)
    assert status == 201, body
    assert stored_holidays(server) == ["2026-10-28"]


def test_a_page_on_another_site_cannot_add_a_holiday(server, browser):
    """The attack the audit found: a page on another origin (here localhost, against the server at 127.0.0.1) makes
    the browser send a text/plain POST, which needs no permission from the server."""
    port = urlsplit(server.url).port
    page = browser.new_context().new_page()
    page.goto(f"http://localhost:{port}/")
    page.wait_for_selector("body[data-ready=true]")
    sent = page.evaluate(  # resolves once the server has answered; a no-cors answer cannot be read, only its type
        """([url, body]) => fetch(url, {method: "POST", mode: "no-cors", body}).then(r => r.type)""",
        [f"http://127.0.0.1:{port}/api/holidays", json.dumps(ADD)],
    )
    assert sent == "opaque"  # the browser sent it cross-site, without asking the server first
    assert stored_holidays(server) == []


@pytest.mark.parametrize("host,allowed", [
    ("127.0.0.1:{port}", True), ("localhost:{port}", True), ("localhost", True),
    ("attacker.example", False), ("attacker.example:{port}", False), ("127.0.0.1.attacker.example", False),
])
def test_a_request_to_an_unknown_host_name_is_refused(server, host, allowed):
    port = urlsplit(server.url).port
    status, _ = send(server, "GET", "/api/status", headers={"Host": host.format(port=port)})
    assert status == (200 if allowed else 400)


def test_a_deploy_can_allow_its_own_host_name(tmp_path, start_server):
    deployed = start_server(tmp_path / "app.db", {"DBD_ALLOWED_HOSTS": "days.example, www.days.example"})
    assert send(deployed, "GET", "/api/status", headers={"Host": "days.example"})[0] == 200
    assert send(deployed, "GET", "/api/status", headers={"Host": "www.days.example"})[0] == 200
    assert send(deployed, "GET", "/api/status", headers={"Host": "other.example"})[0] == 400


@pytest.mark.parametrize("chunked", [False, True], ids=["with-length", "chunked"])
def test_a_body_over_4096_bytes_is_refused_with_413_and_stores_nothing(server, chunked):
    big = json.dumps({**ADD, "pad": "x" * 5000}).encode()
    status, body = send(server, "POST", "/api/holidays", big, {"Content-Type": "application/json"}, chunked)
    assert status == 413, body
    assert stored_holidays(server) == []


def test_a_body_under_the_limit_is_read(server):
    near = json.dumps({**ADD, "pad": "x" * 3900}).encode()
    assert len(near) < 4096
    status, body = send(server, "POST", "/api/holidays", near, {"Content-Type": "application/json"})
    assert status == 201, body


@pytest.mark.parametrize("name", [".env", ".env.local", "app/.env.production"])
def test_environment_files_are_ignored_by_git(name):
    result = subprocess.run(["git", "check-ignore", "-q", name], cwd=ROOT)
    assert result.returncode == 0, f"{name} is not ignored"
