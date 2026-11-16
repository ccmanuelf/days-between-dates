# State

Updated 2026-11-15. A snapshot, replaced at each close (close-session); the history is in git.

## Where the work stands

- `main`: pull request #15 merged (the security audit's four fixes, #14's review points, a guardian for the
  cross-site write fix).
- Branch `docker-only-rules`, for one pull request, on the owner's word of 2026-11-15:
  - `CLAUDE.md` carries the owner's working rules: wording, records and minor gate findings settled by the agent and
    logged; one review pass and one publication check per pull request; no records-only rounds; the plan carried to
    the merge; a stop only for a scope change, a new product decision or an irreversible step outside the plan; a
    command denied by a permission check retried once as one plain command;
  - Docker only: Render and the public demo removed from `SPEC.md` and `CLAUDE.md`; S12 and AC14 withdrawn; the
    passing Docker check is the deployment validation;
  - the app's live-demo notice, its entry in Help, their strings and `GET /api/config` removed; the eight test cases
    of the notice and the route removed, and `tests/test_help.py`'s section list without "demo"; the test servers
    and `scripts/orphans.py` wait for `GET /api/status` instead.

## Checked on this branch (2026-11-15)

- The full suite on this machine: 195 passed (203 on `main`, less the 8 cases of the live-demo tests removed).
- `scripts/orphans.py`: 0 orphans; with `GET /api/config` put back without its caller, it reports that route.

## Pending

- The owner's decision: the cost of a count over years 1 to 9999, reopened on 2026-11-15 as the owner's one open
  product decision, after the earlier pick "Keep as is". Measured on this machine against the running server: 0.08 s
  for Mexico's calendar and 0.16 s for the United States', about 0.001 s for one year.
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

## Last session (2026-11-14 and 2026-11-15)

Done: pull requests #13, #14 and #15 merged; `/security-audit` run; this branch's work and its checks above.
Half-done: this branch's pull request.
