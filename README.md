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
- **English and Spanish**, switchable in the app bar; the choice is stored too.
- **Help and user guide**: a tab beside the counter, with its contents and one short section per feature (the
  counting, the calendars, your own holidays, reversed dates, past years, local election days, the language and the
  sources); "How this is calculated" under the result shows the formula with a worked example. Each worked example
  is a known answer written in the guide's text, and a test reads it from there and counts it again.
- **Light and dark**: the page opens light; the toggle in the app bar switches to dark, and the choice is stored.
- **Accessibility**: each count is written to a status region that screen readers announce; a refused date marks its
  field and shows its message beside the form that sent it; every label sits above its field, and controls are at
  least 24 px tall.

The page follows the owner's visual standard (cobalt for the one main action, warm neutral surfaces, Inter, 6 and 8 px
corners, AG Grid with 32 px rows) and is built on the owner's web starter: Vue 3, Vite and TypeScript, Tailwind CSS 4
with shadcn-vue, served by FastAPI. `DESIGN.md` says how.

Each count is checked against known answers that carry their source (`SPEC.md`, *Known-answer checks*, K1–K11), on
every pull request and every push to `main`.

## Who it's for

A practitioner who lives in spreadsheets and knows some code: an engineer or analyst who wants to see how a count is
defined, wired and verified, as a tested tool instead of a formula whose conventions do not show.

Tester: a Production Scheduler.

## Proven work

Not written yet: a placeholder. Before the app's first release, Claude Code drafts this section and the owner writes the
parts that are the owner's own account, in this order: the problem and what it costs, what was built, how (what AI did
and what the owner did), the top corrections from `JUDGMENT.md`, the result as checked, what the owner would do
differently, and where it applies (`CLAUDE.md`, *Proven work*).

## Run it in Docker

You need Docker with Compose. From the repository folder:

```
docker compose up --build
```

Then open http://127.0.0.1:8765. The image builds the page with Node and runs it with Python, so nothing else is
needed on your machine. If port 8765 is already in use, set another for one run, `BACKEND_PORT=8800 docker compose up
--build`, or keep it in a `.env` file (*Ports*, below). The port is bound to 127.0.0.1, so the app is reachable from
your own machine and not from your network.

Your own holidays and the language and theme choices live in the Docker volume `app-data`, so they survive `docker
compose restart` and `docker compose down`. `docker compose down -v` deletes them.

To clean up, run `docker compose down -v --rmi local`. It removes the container, the volume with your data, and the
app image this folder built. A rebuild after a code change can leave the previous app image behind, untagged, and
Docker's build cache keeps the base image's layers for the next build. Docker's prune commands (`docker image prune`,
`docker builder prune`) clear those for every project on your machine at once, so check `docker system df` first.

## Run it without Docker

Python 3.13 and Node.js 24 (the versions CI uses; `frontend/package.json` lists the Node versions it allows):

```
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
cd frontend
npm ci
npm run build              # the page, into frontend/dist, which the app serves
npm run backend            # the app, http://127.0.0.1:8765
```

While working on the page, keep that backend running and start the page in a second terminal with `npm run dev`
(http://127.0.0.1:5765); requests to `/api` go to the backend.

The database file is created at `DBD_DB_PATH` (default `data/app.db`). The app answers requests addressed to
`127.0.0.1` or `localhost`; to serve it under another host name, list that name in `DBD_ALLOWED_HOSTS` (comma
separated).

## Ports

The app uses two ports, `BACKEND_PORT` (8765: the app, and the Docker container's address) and `FRONTEND_PORT` (5765:
`npm run dev`), with their defaults in `.env.example`. To change them on your machine, copy `.env.example` to `.env`
at the repository's root and edit it; `.env` is not committed. A variable set in your shell wins over `.env`.

## Tests

```
python -m playwright install chromium
cd frontend && npm run typecheck && npm test && npm run build && cd ..
python -m pytest -v        # needs the built page
```

The page's own tests check its types, its language files, its ports, and that no file in `frontend/src` writes a color
of its own outside the visual standard's tokens (the vendored shadcn-vue stylesheet aside). The Python suite runs the
known-answer checks through the API, drives the page in a real browser (Playwright), reads each worked example from the
guide's text and counts it again, and checks that every control on the page reaches a route, every route has a caller,
and every table is written and read
(`scripts/orphans.py`). CI also builds the Docker image and checks the running container, its volume included
(`scripts/docker_check.py`). The specification, with its scenarios, acceptance criteria and sources, is `SPEC.md`.

## Updating the Python pins

`requirements.txt` and `requirements-dev.txt` are generated from the two `.in` files, and pin every package in the
tree, on every platform (`--universal`: a package one platform needs, such as colorama on Windows, is pinned with its
marker). The cutoff makes the tool enforce the two-week rule: it can't see a release younger than two weeks.

```
# On Linux: CUTOFF="$(date -u -d '14 days ago' +%Y-%m-%dT%H:%M:%SZ)"
CUTOFF="$(date -u -v-14d +%Y-%m-%dT%H:%M:%SZ)"
uv pip compile requirements.in --universal --python-version 3.13 --exclude-newer "$CUTOFF" -o requirements.txt
uv pip compile requirements-dev.in --universal --python-version 3.13 --exclude-newer "$CUTOFF" -o requirements-dev.txt
```

A rerun keeps the current pins and updates the cutoff in the file's header. Add `--upgrade` to both commands to move to
the newest allowed releases. If a version named in an `.in` file is too new, the command stops with an error: that is
the rule working. `tests/test_pins.py` checks that each list starts with uv's header and names an `--exclude-newer`
cutoff, that each pin an `.in` file names is in its compiled list at the same version, and that every runtime pin is
tested at the same version.

## Licence

MIT. See `LICENSE`.
