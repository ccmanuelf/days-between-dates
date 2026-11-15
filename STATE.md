# State

Updated 2026-11-15. A snapshot, replaced at each close (close-session); the history is in git.

## Where the work stands

- `main`: pull request #14 merged (accessibility, dark mode, the in-app guide). No live demo is deployed and where it
  is hosted is not decided (the owner, 2026-11-15).
- Branch `audit-fixes`, for one pull request, on the owner's decision of 2026-11-15 after `/security-audit`:
  - a write with a body (adding a holiday, storing the language) must be sent as `application/json` (415 otherwise)
    and be at most 4096 bytes (413 otherwise);
  - a request must be addressed to `127.0.0.1`, `localhost` or a host name listed in `DBD_ALLOWED_HOSTS` (400
    otherwise);
  - `.gitignore` ignores `.env` and `.env.*`;
  - after a failed `GET /api/guide`, the guide shows its texts without an earlier example; a test pins the worked
    examples' words "without your own holidays" in both languages;
  - a guardian, `tests/guardians/test_every_write_reads_its_body_through_json_body.py`, with its fixture and its
    *Known traps* entry in `CLAUDE.md`;
  - tests: `tests/test_hardening.py`, and two new tests (three cases) in `tests/test_help.py`.

## Checked on this branch (2026-11-15)

- The full suite on this machine: 203 passed, 29 of them new test cases.
- A sweep of 25 mutations, each altering one fix, the guardian or its exception rule: each run failed (exit 1), and
  each of the 29 new test cases failed at least once. With the content-type check removed, a page on another origin
  added a holiday through the browser; with it, it did not.
- The guardian flags `app/main.py:82` in `main`'s code (`await request.json()` inside `json_body`), finds no hit in
  this branch's `app/`, and flags each of the 11 marked lines in its fixture.

## Pending

- The owner's decisions, from the audit: (1) on a deployed demo, one database serves every visitor; (2) a count over
  years 1 to 9999 loops over each year (cost not measured).
- `SPEC.md` (D8) and `CLAUDE.md` name Render's free plan for the live demo; the owner said on 2026-11-15 that the host
  is not decided.
- Before the first release or production deploy: the README gains *Proven work* (`CLAUDE.md`, *Proven work*).
- An intermittent failure seen once on 2026-11-14 in
  `test_e3_a_storage_failure_on_an_edit_takes_the_count_off_the_screen[add-unwritable]`; its cause is not
  established.
- `python -m pip install` is not covered by the ask rules (the template has the `python3` form only).
- The `docker` CI job is not a required check; making it one is a branch-protection change, the owner's call.
- `DESIGN.md` restates values from `style.css` and `tokens.css`. No test reads `DESIGN.md` (searched `tests/` and
  `scripts/`), so its copies can drift from those files.

## Decisions (2026-11-15, the owner's)

- After `/security-audit`: merge pull request #14, then fix the audit's top four findings and the review's three
  minor findings in one follow-up pull request, which lands before anything goes public.

## Last session (2026-11-14 and 2026-11-15)

Done: pull requests #13 and #14 merged; `/security-audit` run; this branch's work and its checks above. Half-done:
this branch's pull request.
