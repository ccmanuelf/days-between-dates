"""Guardian: every color in the page's stylesheets is one AC15's contrast check can read.

AC15's tests (tests/test_access.py, CONTRAST) read each text's color and the background behind it with
`getComputedStyle` and parse `rgb()` or `rgba()` only. Chromium reports a `color-mix()`, and colors written in the
newer functions (`oklch()`, `oklab()`, `lab()`, `lch()`, `hwb()`, `color()`), in another form, such as `oklab(0 0 0)`.
On 2026-11-15, during the restyle, a `color-mix()` hover color on the Count button made the error's contrast test
throw ("unparsed color oklab(...)"); it was replaced by a token. The tests catch such a color only on an element on
screen in the state they measure: one on a `:hover` rule of a button they do not hover would pass them, and so would
a color that falls under 4.5:1. CLAUDE.md, *Known traps*, has the entry.

The scan reads every stylesheet in app/static/, comments left out. tests/fixtures/stylesheet_with_unreadable_colors.css
holds the patterns on purpose, each on a line marked "guardian: flag", and each must be flagged.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
STATIC = ROOT / "app/static"
FIXTURE = ROOT / "tests/fixtures/stylesheet_with_unreadable_colors.css"
MARK = "guardian: flag"
INSTEAD = "write the color as a hex value, rgb(), a token from tokens.css or a system color (Canvas, CanvasText)"
UNREADABLE = re.compile(r"(?<![\w-])(color-mix|oklch|oklab|lab|lch|hwb|color)\(", re.IGNORECASE)
COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)

# (file relative to the repository, line) -> reason. No exception is allowed without a reason.
EXCEPTIONS: dict[tuple[str, int], str] = {}


def without_comments(text: str) -> str:
    """The stylesheet with each comment blanked out, its line breaks kept, so line numbers stay true."""
    return COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group()), text)


def hits_in(path: Path) -> list[tuple[str, int, str]]:
    """(file, line, function) for each color function the contrast check cannot read."""
    name = str(path.relative_to(ROOT))
    found = []
    for number, line in enumerate(without_comments(path.read_text()).splitlines(), start=1):
        found += [(name, number, m.group(1)) for m in UNREADABLE.finditer(line)]
    return found


def test_every_stylesheet_color_is_one_the_contrast_check_reads():
    hits = [h for path in sorted(STATIC.glob("*.css")) for h in hits_in(path) if (h[0], h[1]) not in EXCEPTIONS]
    assert not hits, "\n".join(f"{file}:{line}: {function}() — {INSTEAD}" for file, line, function in hits)


def test_the_guardian_flags_its_fixture():
    marked = {n for n, line in enumerate(FIXTURE.read_text().splitlines(), start=1) if MARK in line}
    flagged = {line for _, line, _ in hits_in(FIXTURE)}
    assert marked and flagged == marked, (sorted(marked), sorted(flagged))


def test_every_exception_has_a_reason():
    assert all(reason.strip() for reason in EXCEPTIONS.values())
