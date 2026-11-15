"""Guardian: every write reads its body through `json_body` (app/main.py).

`json_body` refuses a body not sent as application/json (415) and one over 4096 bytes (413). A route that reads its
body with `request.json()`, `.body()`, `.form()` or `.stream()` outside `json_body`, with a Pydantic model, or with
FastAPI's `Body`, `Form`, `File` or `UploadFile`, skips both checks, and a page on another site can again make a
browser write to the app with a text/plain request. Before pull request #15, `json_body` itself read the body with
`request.json()` and checked neither (app/main.py:82 there). CLAUDE.md, *Known traps*, has the entry.

The scan reads every Python file in app/; tests/fixtures/route_reading_its_own_body.py holds the patterns on purpose,
each on a line marked "guardian: flag", and each must be flagged.
"""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
APP = ROOT / "app"
FIXTURE = ROOT / "tests/fixtures/route_reading_its_own_body.py"
MARK = "guardian: flag"
INSTEAD = "read the body with `await json_body(request)` (app/main.py)"

BODY_READS = {"json", "body", "form", "stream"}  # request.<name>() reads the body
BODY_PARAMETERS = {"Body", "Form", "File", "UploadFile"}  # fastapi names that make FastAPI read the body
BODY_MODULES = {"pydantic", "fastapi"}  # imported as a module: a model, or fastapi.Body and the like, can be reached

# (file relative to the repository, enclosing function, pattern) -> reason. No exception is allowed without a reason.
EXCEPTIONS: dict[tuple[str, str, str], str] = {
    ("app/main.py", "json_body", "stream"): "json_body reads the body here, in chunks capped at MAX_BODY, after its "
                                            "content-type check",
}


def enclosing_functions(tree: ast.AST) -> dict[int, str]:
    """The innermost function around each node, by the node's id."""
    owner = {}
    for function in ast.walk(tree):  # outer functions come first, so an inner one overwrites
        if isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for node in ast.walk(function):
                owner[id(node)] = function.name
    return owner


def hits_in(path: Path) -> list[tuple[str, int, str, str, str]]:
    """(file, line, enclosing function, pattern, what was found) for each pattern this scan looks for in one Python
    file: a BODY_READS method called with no arguments, an import of a BODY_MODULES module as a whole, an import from
    pydantic, or a BODY_PARAMETERS name imported from fastapi."""
    tree = ast.parse(path.read_text(), filename=str(path))
    owner = enclosing_functions(tree)
    name = str(path.relative_to(ROOT))
    found = []
    for node in ast.walk(tree):
        where = owner.get(id(node), "")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in BODY_READS:
            if not node.args and not node.keywords:  # json.loads(raw) has an argument; request.json() has none
                found.append((name, node.lineno, where, node.func.attr, f"`.{node.func.attr}()` reads the body"))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in BODY_MODULES:
                    found.append((name, node.lineno, where, "import", f"imports `{alias.name}` as a module"))
        elif isinstance(node, ast.ImportFrom) and node.module:
            top = node.module.split(".")[0]
            if top == "pydantic":
                what = "imports from `pydantic`, whose models FastAPI reads from the body"
                found.append((name, node.lineno, where, "import", what))
            elif top == "fastapi":
                for alias in node.names:
                    if alias.name in BODY_PARAMETERS:
                        what = f"imports `{alias.name}`, which FastAPI reads from the body"
                        found.append((name, node.lineno, where, "import", what))
    return found


def scan(paths: list[Path]) -> list[str]:
    report = []
    for path in sorted(paths):
        for file, line, where, pattern, what in hits_in(path):
            if (file, where, pattern) not in EXCEPTIONS:
                report.append(f"{file}:{line}: {what}; {INSTEAD}")
    return report


def test_every_write_reads_its_body_through_json_body():
    files = list(APP.rglob("*.py"))
    assert len(files) >= 5, files  # the scan reached the app's modules
    assert scan(files) == []


def test_the_guardian_flags_each_pattern_in_its_fixture():
    lines = FIXTURE.read_text().splitlines()
    marked = {number for number, text in enumerate(lines, start=1) if text.rstrip().endswith(MARK)}
    flagged = {int(line.split(":")[1]) for line in scan([FIXTURE])}
    assert len(marked) == 11, marked
    assert flagged == marked, (sorted(marked - flagged), sorted(flagged - marked))


def test_every_exception_has_a_reason():
    assert all(reason.strip() for reason in EXCEPTIONS.values())
