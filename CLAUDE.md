# Days between dates — working context

This repository is public. Everything committed here is published.

## What this app does

A small web app that counts the days between two dates: total days and business days, under both conventions side by
side (the start date not counted · both dates counted). Business days are Monday to Friday minus the active
calendar's holidays: Mexico's mandatory rest days under the federal labour law, or the United States' federal legal
public holidays with their observed days. The user keeps holidays of their own, one list per calendar, in SQLite.
Every convention shows on screen, and every count is checked against a known answer that carries its source. It is
didactic: for a practitioner who lives in spreadsheets and is learning to build a tested tool instead of a formula.
`SPEC.md` is the approved specification: its scenarios, acceptance criteria AC1–AC14 and known answers K1–K11 are the
contract. It is not changed without the owner's approval.

## Definition of done

Functional, does not crash, does not lie. "Lying" means: frontend features never connected to the backend; backend
code that is never called; schemas partially built; tests that check that something exists instead of what it does;
tests of code that is not wired to anything. For calculations, rules and definitions, the result is confirmed against
the known answer every time, not once.

- Every acceptance criterion in `SPEC.md` passes, the scenarios run without crashing, and a live demo exists.
- Each criterion is verified through the real wiring: page → API → SQLite → back, on the running server.
- No orphans: every UI control reaches a backend path that executes; every endpoint has a caller; every schema object
  is written and read. An orphan is a defect, not partial progress.
- The known-answer checks run on every push, against reference values that carry a source.
- Done is shown with evidence (test output, the orphan list, the live demo), never asserted.

## Rules

- Work on feature branches. `main` changes only through a pull request with passing checks.
- No secrets, no credentials, no third-party confidential material.
- When the SPEC is ambiguous, ask. Do not fill the gap with an assumption.
- Scope changes go back to the SPEC and its approval.
- A holiday rule carries its primary source and the date it was checked; a value without a source does not ship.
- A string shown on the page exists in English and in Spanish; a missing one fails a test, never falls back silently.

## Stack

Python and FastAPI, SQLite, one HTML page with a JavaScript module calling the JSON API; tests with pytest and
Playwright for Python. Delivery rung 1: user space, no admin. The SQLite file is created at run time, at
`DBD_DB_PATH` (default `data/app.db`), and never committed. Live demo: Render's free plan, whose storage resets on
restart, which the demo page says (S12, AC14). Licence: MIT. Interface: English and Spanish.

## Commands

```
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
python -m playwright install chromium
python -m uvicorn app.main:app        # http://127.0.0.1:8000
python -m pytest -v
```

`CHROMIUM_PATH`, if set, points the browser tests to a Chromium already installed.
