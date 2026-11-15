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
