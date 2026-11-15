# State

Updated 2026-11-14. A snapshot, replaced at each close (close-session); the history is in git.

## Where the work stands

- Branch `accessibility-dark-mode-guide`, for one pull request. On `main` before it (pull request #13): the app
  template's process files, `DESIGN.md`, the motion tokens, Docker and its CI job, the README.
- This branch adds, on the owner's plan and SPEC approval of 2026-11-14 (`SPEC.md`, *Approval*):
  - the third review of #13's two minor points: `scripts/docker_check.py`'s by-hand steps run under their own compose
    project, `dbd-check`; `JUDGMENT.md` records the security-audit skill's narrowed claim;
  - S13, dark mode: four color tokens in `app/static/tokens.css`, read by `style.css`, with dark values under the
    system's dark scheme, and `color-scheme: light dark` for the page and its controls;
  - S14, accessibility: a status region announces each count and its notices; each Remove button's name includes its
    date; buttons, fields, lists and panel toggles are at least 24 px tall; each label is grouped with its field;
  - S15 and S16, the guide: a Help panel with one section for each feature SPEC S15 lists, and "How this is
    calculated" for total and business days, whose worked examples come from `GET /api/guide` (`app/guide.py`),
    counted by `app/counting.py` with no holidays of the user's own each time a panel opens;
  - after the first publication check: the dark placeholders take `--note-text` (2.43:1 before, under AC15's 4.5:1),
    and the contrast tests also measure placeholders, the light-mode error and the live-demo notice;
  - tests: `tests/test_guide.py` (the examples against the known answers), `tests/test_access.py` (S13, S14),
    `tests/test_help.py` (S15, S16, AC17, AC18); the orphan check drives the three new panel toggles.

## Checked on this branch (2026-11-14)

- The full test suite on this machine (Python 3.13 in `.venv`, Chromium 1208 through `CHROMIUM_PATH`): 174 passed,
  35 of them new (`tests/test_guide.py` 4, `tests/test_access.py` 22, `tests/test_help.py` 9). One earlier full run
  on the same code had one failure in an existing test (*Pending*).
- A final sweep of 25 mutations on this branch's code, each altering one guarantee and then restored and compared: each
  run failed (exit 1), and all 35 new tests failed at least once across the sweep. Among the mutations: a guide range
  changed, own holidays let into the examples, a dark note color too dark, the dark placeholder rule removed, a light
  table border changed, no minimum height, the calendar label out of its group, no announcement, a digit typed into
  the guide, the guide longer than the page; and the orphan check reports 4 orphans when the panels open without
  asking the API, 0 on this branch.

## Pending

- Before merging this branch: the owner runs `/security-audit` (he looked at the branch running in Docker on
  2026-11-14).
- Before the first release or production deploy: the README gains *Proven work* (`CLAUDE.md`, *Proven work*),
  drafted with the owner's parts marked and never committed with a marker left.
- The live demo on Render (S12, AC14) was not checked in this round. After the next deploy, check that it answers
  200 for `/static/tokens.css` and `/api/guide`, and that its page renders.
- An intermittent failure: in one full local run on 2026-11-14,
  `test_e3_a_storage_failure_on_an_edit_takes_the_count_off_the_screen[add-unwritable]` saw "The server did not
  answer" where the storage error was expected, and the server logged no `POST /api/holidays`. Run apart from the
  suite, the test's four cases passed in each of 10 runs. The test, `tests/conftest.py`, `app/storage.py`, the
  `add_holiday` route and the page's `api`, `addHoliday`, `showFailure`, `showError` and `errorText` are unchanged on
  this branch; `hideResult` now also clears the status region. Its cause is not established.
- `python -m pip install` is not covered by the ask rules (the template has the `python3` form only).
- The `docker` job is not a required check; making it one is a branch-protection change, the owner's call.
- `DESIGN.md` restates values from `style.css` and `tokens.css`. No test reads `DESIGN.md` (searched `tests/` and
  `scripts/`), so its copies can drift from those files.

## Decisions (2026-11-14, the owner's)

- SPEC S13–S16 and AC15–AC18 approved; dark mode follows the system; worked examples are counted by the API.
- Design tokens may ship before a rule reads them (`CLAUDE.md`, *Definition of done*; `JUDGMENT.md`).
- Docker is packaging; a `docker` job in CI, not a required check.

## Last session (2026-11-14)

Done: pull request #13 merged; this branch's work and its checks above; the owner looked at the branch running in
Docker. Half-done: `/security-audit`, before merging. Learned: a mutation run that restores a file with
`git checkout` cannot restore an untracked file, so mutations restore from a copy and compare it with the copy; and a
claim of "every text" rests on what the test enumerates, so its skipped class (placeholders) is where to look.
