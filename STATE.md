# State

Updated 2026-11-15. A snapshot, replaced at each close (close-session); the history is in git.

## Where the work stands

- `main`: pull request #16 merged (Docker only, with no public demo or external host; the owner's working rules in
  `CLAUDE.md`).
- Branch `years-1950-2150`, for one pull request, on the owner's decision of 2026-11-15: the app accepts dates from
  1950-01-01 to 2150-12-31 (`SPEC.md`, *Expectations* and E1); K11 moves to the new last dates, US, 2150-12-24 →
  2150-12-31; `parse_date` refuses a date outside those years, naming them, and the page's message names them in
  English and Spanish; removing an own holiday still accepts a day stored outside them before the change; the tests
  pinned to year 9999 move to 2150, and those of the date modules' own limits stay, named for the date type.

## Checked on this branch (2026-11-15)

- The full suite on this machine: 204 passed (195 on `main`, and 9 new cases).
- The new refusal and text tests failed on `main`'s code (7 failed), before the change; the removal test failed
  before its fix.
- Eight mutations (each end one year off either way, no check, removal held to the limit, either language's text
  left at 1 to 9999): each made its tests fail.

## Pending

- Before the first release: the README gains *Proven work* (`CLAUDE.md`, *Proven work*).
- An intermittent failure seen once on 2026-11-14 in
  `test_e3_a_storage_failure_on_an_edit_takes_the_count_off_the_screen[add-unwritable]`; its cause is not
  established.
- `python -m pip install` is not covered by the ask rules (the template has the `python3` form only).
- The `docker` CI job, now the deployment validation, is not a required check; making it one is a branch-protection
  change, the owner's call.
- `DESIGN.md` restates values from `style.css` and `tokens.css`. No test reads `DESIGN.md` (searched `tests/` and
  `scripts/`), so its copies can drift from those files.

## Decisions (2026-11-15, the owner's)

- After `/security-audit`: merge pull request #14, then fix the audit's top four findings and the review's three
  minor findings in one follow-up pull request (#15, merged).
- The working rules now in `CLAUDE.md`, effective 2026-11-15.
- Docker only, with no public demo or external host; the passing Docker check is the deployment validation (SPEC,
  *Approval*, 2026-11-15). The question of one database serving every visitor of a demo is dropped.
- The years accepted: 1950 to 2150 (SPEC, *Approval*, 2026-11-15), the owner's answer to the cost of a count over
  years 1 to 9999.

## Last session (2026-11-14 and 2026-11-15)

Done: pull requests #13 to #16 merged; `/security-audit` run; this branch's work and its checks above.
Half-done: this branch's pull request.
