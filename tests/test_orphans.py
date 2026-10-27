"""The orphan check runs on every pull request and every push to main (plan step 7, AC10), and catches an orphan."""

import importlib.util
import re
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts/orphans.py"
spec = importlib.util.spec_from_file_location("orphans", SCRIPT)
orphans = importlib.util.module_from_spec(spec)
spec.loader.exec_module(orphans)


def test_the_app_has_no_orphans():
    assert orphans.find_orphans() == []


def test_a_route_without_a_caller_is_reported():
    routes = [("GET", "/api/used", re.compile("^/api/used$")), ("GET", "/api/unused", re.compile("^/api/unused$"))]
    assert orphans.route_orphans(routes, [("GET", "/api/used", 200)]) == ["route without a caller: GET /api/unused"]


def test_a_route_that_does_not_execute_is_reported():
    routes = [("DELETE", "/api/x/{id}", re.compile("^/api/x/(?P<id>[^/]+)$"))]
    found = orphans.route_orphans(routes, [("DELETE", "/api/x/1", 405)])
    assert found == ["route without a caller: DELETE /api/x/{id}"]


def test_a_table_written_but_never_read_is_reported():
    sql = '"CREATE TABLE IF NOT EXISTS log (line TEXT)" "INSERT INTO log (line) VALUES (?)"'
    assert orphans.table_orphans(sql) == ["table never read: log"]
