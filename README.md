# Days between dates

A small web app that counts the days between two dates: total days and business days, shown side by side under the
two usual conventions (the start date not counted · both dates counted).

- **Business days** are Monday to Friday minus the active calendar's holidays: Mexico's mandatory rest days under the
  federal labour law (Ley Federal del Trabajo, art. 74), or the United States' federal legal public holidays
  (5 U.S.C. § 6103) with their observed days.
- **Your own holidays**: add or remove days, one list per calendar. They are stored in SQLite and survive a restart.
- **Every convention on screen**: the active calendar is named, reversed dates are swapped with a notice, a range that
  reaches into past years says the holidays use today's rules, and each calendar lists its sources and the date its
  rules were checked.
- **English and Spanish**, switchable; the choice is stored too.
- **Help and the formulas**: a Help panel explains the counting, the calendars, your own holidays, reversed dates,
  past years, local election days, the language, the live demo and the sources, and "How this is calculated" under
  the result shows the formula with a worked example. Each worked example is a known answer, counted by the app's
  own code when the panel opens and checked against the known answers by the tests.
- **Dark mode and accessibility**: the page follows the system's dark setting; each count is written to a status
  region that screen readers announce; controls are at least 24 px tall, and each label stays with its field on a
  narrow screen.

Each count is checked against known answers that carry their source (`SPEC.md`, *Known-answer checks*, K1–K11), on
every pull request and every push to `main`.

## Who it's for

A practitioner who lives in spreadsheets and knows some code: an engineer or analyst who wants to see how a count is
defined, wired and verified, as a tested tool instead of a formula whose conventions do not show.

Tester: a Production Scheduler.

## Run it in Docker

You need Docker with Compose. From the repository folder:

```
docker compose up --build
```

Then open http://127.0.0.1:8000. If port 8000 is already in use on your machine, pick another:

```
DBD_PORT=8765 docker compose up --build
```

and open http://127.0.0.1:8765. The port is bound to 127.0.0.1, so the app is reachable from your own machine and
not from your network.

Your own holidays and the language choice live in the Docker volume `app-data`, so they survive `docker compose
restart` and `docker compose down`. `docker compose down -v` deletes them.

To clean up, run `docker compose down -v --rmi local`. It removes the container, the volume with your data, and the
app image this folder built. A rebuild after a code change can leave the previous app image behind, untagged, and
Docker's build cache keeps the base image's layers for the next build. Docker's prune commands (`docker image prune`,
`docker builder prune`) clear those for every project on your machine at once, so check `docker system df` first.

## Run it without Docker

Python 3.13 (the version CI uses):

```
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
python -m uvicorn app.main:app        # http://127.0.0.1:8000
```

The database file is created at `DBD_DB_PATH` (default `data/app.db`).

## Tests

```
python -m playwright install chromium
python -m pytest -v
```

The suite runs the known-answer checks through the API, drives the page in a real browser (Playwright), and checks
that every control on the page reaches a route, every route has a caller, and every table is written and read
(`scripts/orphans.py`). CI also builds the Docker image and checks the running container, its volume included
(`scripts/docker_check.py`). The specification, with its scenarios, acceptance criteria and sources, is `SPEC.md`.

## Licence

MIT. See `LICENSE`.
