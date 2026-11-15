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
    `index.html` for `transition`, `animation` and `keyframes` finds no match, so no motion uses them yet (allowed by
    the design-token exception in `CLAUDE.md`, *Definition of done*);
  - `Dockerfile`, `compose.yaml` and `.dockerignore`: the app in one container, its database in the named volume
    `app-data`, the port set by `DBD_PORT` (default 8000) and bound to 127.0.0.1; Docker is packaging, so `SPEC.md`
    is unchanged;
  - `scripts/docker_check.py` and a `docker` job in CI, not a required check: the job builds and starts the app with
    compose, checks the page, its assets, K1 through the API and a stored holiday, recreates the container, checks
    the holiday came back from the volume, and removes the container, volume and image;
  - `README.md`: what the app does, who it is for, how to run it in Docker and without, how to clean up, the tests,
    the licence;
  - `JUDGMENT.md`: its first three entries, from this pull request's reviews.

## Checked on this branch (2026-11-14)

- The `docker` job's steps, run by hand on this machine: both checks passed. They also failed (exit 1) on two
  altered copies: one whose `.dockerignore` left `app/static/tokens.css` out of the image (404), and one whose
  `compose.yaml` had no volume (the stored holiday was gone after the container was recreated). Three altered copies
  of `scripts/docker_check.py`, each changing one line, failed (exit 1) on the check they target: the page check, K1
  (expected business days 4 · 4) and the stored holiday (an invalid date, refused with 422).
- CI ran the `docker` job on this pull request: its eight checks passed, and its clean-up removed the container, the
  volume, the network and the image.
- Against the container on an empty volume, a local script that is not in this repository checked K1–K11 through
  `/api/count` (K8a, a list of days, not replayed), K4's swap, the past-years flag both ways, E1 and E2 refusals,
  own holidays stored, listed after `docker compose restart`, kept out of the other calendar and removed, the
  language choice after a restart, the demo flag off, and each calendar's sources; the script failed (exit 1) when
  one expected value was altered. `docker compose restart` keeps the container's own files, so these restarts do not
  test the volume; the `docker` job's recreate step does.
- A container started with `DBD_LIVE_DEMO=1` answered `{"live_demo":true}` and its page showed the live-demo notice;
  the compose stack answered `{"live_demo":false}`.
- In headless Chromium against the compose stack: the page counted K1 in Mexico (4 · 5 and 4 · 5), linked
  `tokens.css` (`--motion-scale` read 1), switched to Spanish (*Días hábiles*, counts unchanged), had no horizontal
  scroll at 375 px and logged no console errors.
- The test suite was not run locally on this branch (no local environment); CI runs it on the pull request.

## Pending

- Before the first release or production deploy: the owner runs `/security-audit`; the README gains *Proven work*
  (`CLAUDE.md`, *Proven work*), drafted with the owner's parts marked and never committed with a marker left.
- The live demo on Render (S12, AC14) was not checked in this round. This branch changes the page the demo serves
  (`index.html` now links `/static/tokens.css`): after the next deploy, check that the demo answers 200 for
  `/static/tokens.css` and that its page renders.
- Found by the design audit of 2026-11-14, not fixed (outside this round's scope): results and notices that appear
  after a count are not announced to screen readers (no live region); every "Remove" button has the same name,
  without its date; buttons and fields measured 19–21 px tall (headless Chromium, 375×812 viewport, each element's
  bounding box), under the 24 px of WCAG 2.2's target-size minimum (2.5.8), whose spacing exception was not checked;
  at 375 px the Calendar label can sit on one line and its list on the next; colors are fixed values, with no dark
  mode.
- `python -m pip install` is not covered by the ask rules (the template has the `python3` form only).
- The `docker` job is not a required check; making it one is a branch-protection change, the owner's call.
- `DESIGN.md` restates values from `style.css` in its frontmatter, as the DESIGN.md format asks, and in its
  *Colors*, *Typography*, *Layout* and *Components* sections, and from `tokens.css` in its *Do's and Don'ts*; no check
  keeps the copies in step.

## Decisions (2026-11-14, the owner's)

- Design tokens may ship before a rule reads them (`CLAUDE.md`, *Definition of done*; `JUDGMENT.md`).
- Docker is packaging; `SPEC.md` is unchanged.
- A `docker` job in CI, not a required check (`JUDGMENT.md`).
- The corrected Docker record gets a `JUDGMENT.md` entry.

## Last session (2026-11-14)

Done: the template sync, `DESIGN.md` and the motion tokens, Docker and its CI job, the README, the checks above.
Half-done: none on this branch. Learned: port 8000 can be taken on the working machine, so the compose file reads
`DBD_PORT`; a check script that stores data leaves it in the volume, so a second script that expects an empty
database runs on a fresh volume.
