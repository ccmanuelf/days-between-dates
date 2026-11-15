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
- **2026-11-14 — the security-audit skill's read-only claim narrowed** (pull request #13; this entry was added in the
  pull request after it)
  - Produced: `.claude/skills/security-audit/SKILL.md`, copied from the app template, said that while the audit runs
    "it cannot edit or write files, run shell commands or reach the network (the tools for those are removed by
    `disallowed-tools`)".
  - Wrong: that list names six built-in tools; tools from MCP servers and the Agent tool are not on it, so the
    sentence claimed an enforcement the list does not give.
  - Caught by: the reviewer agent, second full review of pull request #13.
  - Decision: the owner's pick, 2026-11-14: "Fix minors, then review".
- **2026-11-14 — the dark placeholders brought to 4.5:1** (pull request #14)
  - Produced: dark mode left the date fields' placeholders in the browser's dark default, rgb(117, 117, 117) on the
    field's rgb(59, 59, 59), a contrast of 2.43:1; the contrast test measured the elements' text, not placeholders.
  - Wrong: AC15 asks each text for at least 4.5:1, and a placeholder is text.
  - Caught by: the reviewer agent, in the publication check before the branch's first push, which found the
    sentence "Every text keeps at least 4.5:1" broader than the test behind it.
  - Decision: the owner's pick, 2026-11-14: "Fix it, extend the test (Recommended)".
- **2026-11-15 — the announcement test made independent of the year** (pull request #14)
  - Produced: a test of the screen-reader announcement that counted 2026 ranges (K1, K4) and expected its text
    without the past-years notice.
  - Wrong: the app adds that notice to a range that includes a year before the current one, so from 2027-01-01 the
    test would fail on correct code, and with it CI's `test` check, which `main` requires; no test in `tests/`
    checked the announcement for that notice (searched for `notice_past_years`).
  - Caught by: the reviewer agent, full review of pull request #14.
  - Decision: the owner's pick, 2026-11-15: "Fix all, add entries (Recommended)".
- **2026-11-15 — the worked examples say they leave out the user's own holidays** (pull request #14)
  - Produced: worked examples labelled "Example (K1):" and so on, counted without the user's own holidays, with
    nothing on the page saying so.
  - Wrong: with a holiday of one's own on a weekday inside the business example's range, the user's business-day
    count can differ from the example's, a convention not shown on screen in an app built to show them.
  - Caught by: the reviewer agent, full review of pull request #14.
  - Decision: the owner's pick, 2026-11-15: "Add the words (Recommended)".
- **2026-11-15 — the security audit's four fixes** (pull request #15)
  - Produced: write routes that read a request body as JSON whatever its declared content type and size, a server
    that answered any host name, and a `.gitignore` with no entry for environment files.
  - Wrong: a page on another site could make a visitor's browser add a holiday to the app on their machine, with a
    `text/plain` request the browser sends without asking the server first (`tests/test_hardening.py` shows it).
  - Caught by: `/security-audit`, run by the owner before publishing.
  - Decision: the owner's words, 2026-11-15: "Decision on the audit: merge, then fix."
- **2026-11-15 — a failed request for the worked examples shows no earlier example** (pull request #15)
  - Produced: after a failed `GET /api/guide`, Help and "How this is calculated" kept the examples from an earlier
    opening.
  - Wrong: S16 asks for an example counted by the app's code when the panel opens.
  - Caught by: the reviewer agent, full review rerun of pull request #14.
  - Decision: the owner's words, 2026-11-15: "plus the review's 3 minor findings".
