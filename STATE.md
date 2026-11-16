# State

Updated 2026-11-16. A snapshot, replaced at each close (close-session); the history is in git.

## Where the work stands

- `main`: pull request #22 merged (the page's icon). Before it: #21, the rebuild on the owner's web starter following
  the visual standard in full; #20, the Python pins, the documentation routes off and the app template's wording.
- Branch `proven-work`, for one pull request, on the owner's word of 2026-11-16: the README's *Proven work* section,
  written by the agent from the records (`SPEC.md`, `STATE.md`, `JUDGMENT.md`, the merged pull requests), with the
  owner's part described from them; its item on what the owner would do differently is left out, on the owner's
  instruction, since no record supports it. Three screenshots with made-up data in `docs/proven-work/`.
- The app runs in Docker at http://127.0.0.1:8765 for the owner's review, built from `main` at a7fa2f5; its data
  volume is kept, and this project's other Docker leftovers are pruned.

## Checked on this branch (2026-11-16)

- Each claim in the section traced to its record; claims the records could not support were narrowed or left out.
- The three screenshots looked at: the page only, with made-up data (the result's range an example chosen to show both
notices; the guide's ranges the SPEC's known answers; an example own holiday); no address bar, user name or local path.
The CI counts the section cites come from run 43981321389, on pull request #22's head 09135e6.

## Pending

- An intermittent failure seen once on 2026-11-14 in
  `test_e3_a_storage_failure_on_an_edit_takes_the_count_off_the_screen[add-unwritable]`; its cause is not
  established.
- `python -m pip install` is not covered by the ask rules (the template has the `python3` form only).
- `DESIGN.md` restates values from `frontend/src/design-system/tokens.css`. No test reads `DESIGN.md` (searched
  `tests/` and `scripts/`), so its copies can drift from that file.
- Notes outside this repository still say existing apps are not restyled; they are updated in their own session.

## Decisions (the owner's)

- After `/security-audit`: merge pull request #14, then fix the audit's top four findings and the review's three
  minor findings in one follow-up pull request (#15, merged).
- The working rules now in `CLAUDE.md`, effective 2026-11-15.
- Docker only, with no public demo or external host; the passing Docker check is the deployment validation (SPEC,
  *Approval*, 2026-11-15).
- The years accepted: 1950 to 2150 (SPEC, *Approval*, 2026-11-15).
- The `docker` job a required check, and nothing left that slowly eats space (#18, merged).
- The restyle and the user guide; the guide no more elaborate than the app (SPEC, *Approval*, 2026-11-15).
- 2026-11-16: the app reflects the whole foundation, rebuilt on the web starter, fixing the audit's gaps, the SPEC
  and CI changes they named included; the starter's downloads approved
  (a Node base image, the npm packages from `npm ci`, the PyPI lookups and installs for the fully pinned Python list).
- 2026-11-16: the page's icon; the README's *Proven work* section written by the agent from the records, with no
  brackets left and nothing the records cannot support.

## Last session (2026-11-15 and 2026-11-16)

Done: pull requests #18 to #22 merged; the foundation audit, the rebuild and the icon; the app run in Docker for
review; this branch's work and its checks above.
Half-done: this branch's pull request, to be merged as the session's last step.
