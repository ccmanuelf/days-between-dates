# Judgment log

What reviews changed, one entry per change (`CLAUDE.md`, *Judgment log*).

- **2026-11-14 — motion tokens kept before any rule reads them** (pull request #13)
  - Produced: `app/static/tokens.css`, six motion tokens linked from the page; no rule in `style.css`, `app.js` or
    `index.html` reads them (searched for `var(--` and the six token names).
  - Wrong: the reviewer read definitions with no reader as the CSS form of the definition of done's "backend code
    that is never called", and as a placeholder under its "No half-built schemas, stubs or placeholder data"; that
    tension with the owner's request for the file was not raised before the file was written.
  - Caught by: the reviewer agent, full review of pull request #13.
  - Decision: the owner's pick, 2026-11-14: "Keep, add exception (Recommended)".
- **2026-11-14 — a Docker job in CI** (pull request #13)
  - Produced: a `Dockerfile` and `compose.yaml` checked by hand, with no lasting check.
  - Wrong: `.github/workflows/ci.yml` had no step that built the image, so a change that breaks `docker compose up`
    (a runtime file outside `app/`, which `.dockerignore` leaves out of the build) would still pass CI.
  - Caught by: the reviewer agent, full review of pull request #13.
  - Decision: the owner's pick, 2026-11-14: "Add job, not required (Recommended)".
- **2026-11-14 — the Docker record narrowed to its evidence** (pull request #13; the change is in its second commit,
  this entry in its third)
  - Produced: `STATE.md` and the pull request body credited a local script with checking the live-demo flag on, and
    counted the script's `docker compose restart` checks as tests of the volume.
  - Wrong: the script checked the flag off only; the flag on was checked by a separate run. `docker compose restart`
    keeps the container's own files, so those checks would pass with no volume.
  - Caught by: the reviewer agent, full review of pull request #13.
  - Decision: the owner's pick, 2026-11-14: "Add an entry (Recommended)".
