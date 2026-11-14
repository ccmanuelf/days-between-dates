# State

Updated 2026-11-14. A snapshot, replaced at each close (close-session); the history is in git.

## Where the work stands

- Branch `template-sync-docker-readme`, for one pull request. On `main` before it: the app built to `SPEC.md`, its
  test suite run by CI on every pull request and every push to `main` (the live demo, AC14, was not checked in this
  round), and the ask rules in `.claude/settings.json`.
- This branch adds:
  - from the app template: `CLAUDE.md`'s *Where the agent stops*, the clash and gate rules, *Publication check* (with
    its check of "only", "none", "nothing", "all" and "never" used as claims in prose), *Guardians*, *Judgment log*,
    *Proven work* and *Known traps*; the reviewer agent (`.claude/agents/reviewer.md`); the open-session,
    close-session and security-audit skills (`.claude/skills/`);
  - `DESIGN.md`: the page's look as built, charts drawn with ECharts, motion through the tokens;
  - `app/static/tokens.css`: the motion tokens, linked from the page; a search of `style.css`, `app.js` and
    `index.html` for `transition`, `animation` and `keyframes` finds no match, so no motion uses them yet;
  - `Dockerfile`, `compose.yaml` and `.dockerignore`: the app in one container, its database in the named volume
    `app-data`, the port set by `DBD_PORT` (default 8000) and bound to 127.0.0.1;
  - `README.md`: what the app does, who it is for, how to run it in Docker and without, the tests, the licence.

## Checked on this branch (2026-11-14)

- Docker: the image built from `python:3.13-slim`; the container runs as a user without root rights. Against the
  running container: K1–K11 through `/api/count` (K8a not replayed, it is a list of days, not a range), K4's swap,
  the past-years flag both ways, E1 and E2 refusals, own holidays added, listed after a restart, kept out of the other
  calendar and removed after a restart, the language choice kept after a restart, the demo flag off locally and on
  with `DBD_LIVE_DEMO=1`, and each calendar's sources: these checks passed, run by a local script that is not in
  this repository, and the same script failed (exit 1) when one expected value was altered. In a headless browser:
  the page counted K1 in Mexico, switched to the United States, added a holiday (business days 3 · 4), switched to
  Spanish (*Días hábiles* and the art. 715 note shown, counts unchanged), showed the live-demo notice in demo mode,
  had no console errors, and had no horizontal scroll at 375 px.
  `docker compose down` kept an added holiday; `docker compose down -v` deleted it.
- The test suite was not run locally on this branch (no local environment); CI runs it on the pull request.

## Pending

- Before the first release or production deploy: the owner runs `/security-audit`; the README gains *Proven work*
  (`CLAUDE.md`, *Proven work*), drafted with the owner's parts marked and never committed with a marker left.
- The live demo on Render (S12, AC14) was not checked in this round.
- Found by the design audit of 2026-11-14, not fixed (outside this round's scope): results and notices that appear
  after a count are not announced to screen readers (no live region); every "Remove" button has the same name,
  without its date; buttons and fields measured 19–21 px tall (headless Chromium, 375×812 viewport, each element's
  bounding box), under the 24 px of WCAG 2.2's target-size minimum (2.5.8), whose spacing exception was not checked;
  at 375 px the Calendar label can sit on one line and its list on the next; colors are fixed values, with no dark
  mode.
- `python -m pip install` is not covered by the ask rules (the template has the `python3` form only).

## Last session (2026-11-14)

Done: the template sync, `DESIGN.md` and the motion tokens, Docker, the README, the checks above. Half-done: none on
this branch. Learned: port 8000 can be taken on the working machine, so the compose file reads `DBD_PORT`.
