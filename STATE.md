# State

Updated 2026-11-16. A snapshot, replaced at each close (close-session); the history is in git.

## Where the work stands

- `main`: pull request #21 merged: the page rebuilt on the owner's web starter and following the visual standard in
  full (an app bar with the storage status, the EN/ES switch and a remembered light/dark toggle; labels above fields;
  AG Grids; the guide a tab whose worked examples are read from its text by `tests/test_guide.py`; ports 8765 and
  5765; a two-stage Docker image).
- Branch `favicon`, for one pull request, on the owner's word of 2026-11-16: the page gets an icon
  (`frontend/public/favicon.svg`, a calendar page in the standard's cobalt, linked from `index.html`), so its load gets
  no 404; a page test checks that, on load, no request fails or answers with an error status, no uncaught error is
  thrown and no console message is an error, and that the icon is served in `tokens.css`'s cobalt; the Docker check
  asks for the icon.
- The app runs in Docker at http://127.0.0.1:8765 for the owner's review, rebuilt from `main` after each merge; its
  data volume is kept.

## Checked on this branch (2026-11-16)

- The new page test failed before the change: the browser's request for `/favicon.ico` answered 404. It also failed
  on each of four mutations: the icon's cobalt not the token's, an uncaught error on load, a request that gets no
  answer, the icon's link left out.
- The page: type check clean; 112 unit tests passed. The full Python suite on this machine, on the built page: 237
  passed (236 on `main`).
- The icon, looked at from 16 to 128 px: not committed.

## Pending

- An intermittent failure seen once on 2026-11-14 in
  `test_e3_a_storage_failure_on_an_edit_takes_the_count_off_the_screen[add-unwritable]`; its cause is not
  established.
- `python -m pip install` is not covered by the ask rules (the template has the `python3` form only).
- `DESIGN.md` restates values from `style.css` and `tokens.css`. No test reads `DESIGN.md` (searched `tests/` and
  `scripts/`), so its copies can drift from those files.
- Notes outside this repository still say existing apps are not restyled; they are updated in their own session.
- *Proven work*: due once the app meets the definition of done, before its first release or production deploy; the
  README holds a marked placeholder until the owner writes it (about 15 minutes).

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

## Last session (2026-11-15 and 2026-11-16)

Done: pull requests #18 to #21 merged; the foundation audit and the rebuild; the app run in Docker for review; this
branch's work and its checks above.
Half-done: this branch's pull request.
