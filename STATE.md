# State

Updated 2026-11-16. A snapshot, replaced at each close (close-session); the history is in git.

## Where the work stands

- `main`: pull request #19 merged (the restyle within the old palette, and Help as a user guide).
- The owner's decision of 2026-11-16: this app must reflect the whole foundation (the visual standard, the web
  starter, the app template, the quality gates, the four adds, the User Guide rule, the publication check); the old
  "not restyled" line in `DESIGN.md` was wrong. An audit listed the gaps between this app and the foundation; the
  owner chose to rebuild on the web starter.
- Branch `foundation-hygiene`, for one pull request: the Python pins compiled from `.in` files with a two-week
  cutoff and `--universal`, with `tests/test_pins.py`; FastAPI's documentation routes turned off, with a test that
  each answers 404 (the orphan check's name filter for them was dead code: they were never `APIRoute`s, so it is
  removed); `CLAUDE.md` and the security-audit skill in the app template's wording (the audit before each
  publish, the merge rule's last sentence, *Proven work*'s trigger, the guardians' linter).
- Next: the rebuild on the web starter, a pull request of its own.
- The app from `main` at 6e52eb8 runs in Docker at http://127.0.0.1:8765 for the owner's review; nothing is pruned
  until the owner says the review is done.

## Checked on this branch (2026-11-16)

- The new tests failed before the change: the documentation routes answered (4 cases), and the header test failed
  on `main`'s two hand-written lists. Each pin test also failed on the drift it guards, on a copy: a shared pin
  changed in one list, and a pin raised by hand in the compiled lists only.
- The full suite on this machine: 220 passed (213 on `main`, in CI run 43806269163).

## Pending

- An intermittent failure seen once on 2026-11-14 in
  `test_e3_a_storage_failure_on_an_edit_takes_the_count_off_the_screen[add-unwritable]`; its cause is not
  established.
- `python -m pip install` is not covered by the ask rules (the template has the `python3` form only).
- `DESIGN.md` restates values from `style.css` and `tokens.css`. No test reads `DESIGN.md` (searched `tests/` and
  `scripts/`), so its copies can drift from those files.
- `DESIGN.md` still says the app predates the visual standard and is not restyled to its palette; the rebuild's pull
  request rewrites it from the standard.
- Notes outside this repository still say existing apps are not restyled; they are updated in their own session.
- *Proven work*: due once the app meets the definition of done, before its first release or production deploy; the
  owner writes his parts (about 15 minutes).

## Decisions (the owner's)

- After `/security-audit`: merge pull request #14, then fix the audit's top four findings and the review's three
  minor findings in one follow-up pull request (#15, merged).
- The working rules now in `CLAUDE.md`, effective 2026-11-15.
- Docker only, with no public demo or external host; the passing Docker check is the deployment validation (SPEC,
  *Approval*, 2026-11-15).
- The years accepted: 1950 to 2150 (SPEC, *Approval*, 2026-11-15).
- The `docker` job a required check, and nothing left that slowly eats space (#18, merged).
- The restyle and the user guide; the guide no more elaborate than the app (SPEC, *Approval*, 2026-11-15).
- 2026-11-16: the app reflects the whole foundation, rebuilt on the web starter; the starter's downloads approved
  (a Node base image, the npm packages from `npm ci`, the PyPI lookups and installs for the fully pinned Python list).

## Last session (2026-11-15 and 2026-11-16)

Done: pull requests #18 and #19 merged; the app run in Docker for review; the foundation audit; this branch's
work and its checks above.
Half-done: this branch's pull request; the rebuild.
