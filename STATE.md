# State

Updated 2026-11-16. A snapshot, replaced at each close (close-session); the history is in git.

## Where the work stands

- `main`: pull request #20 merged (the Python pins compiled with a two-week cutoff, the documentation routes off,
  `CLAUDE.md` in the app template's wording).
- Branch `web-starter`, for one pull request, on the owner's decision of 2026-11-16 (the app reflects the whole
  foundation; rebuilt on the web starter): the page rebuilt in Vue 3 with the starter's shell, components and the
  visual standard's files unchanged; an app bar with the storage status, the EN/ES switch and a theme toggle (light by
  default, the choice stored through the API); labels above fields; the result and the own holidays in AG Grids; the
  guide a tab, its worked examples written in its text and read by `tests/test_guide.py`; `/api/guide` removed and
  `/api/theme` added; the ports `BACKEND_PORT` 8765 and `FRONTEND_PORT` 5765; a two-stage Docker image (Node builds
  the page); CI checks the page's types and unit tests and builds it before the Python suite; `SPEC.md` (S13–S16,
  AC10, AC15–AC18, the web interface), `DESIGN.md` (rewritten from the standard), `CLAUDE.md` (the *User Guide*
  section), README.
- The app from `main` at 6e52eb8 runs in Docker at http://127.0.0.1:8765 for the owner's review; after this branch
  merges it is rebuilt from `main` at the same address. Nothing of this project's Docker data is pruned until the
  owner says the review is done.

## Checked on this branch (2026-11-16)

- The page: type check clean; 117 unit tests passed (the starter's, adapted: ports, locales, the color source, the
  grid's row height, the button's outline default).
- The full Python suite on this machine, on the built page: 233 passed (220 on `main`).
- Twelve mutations, each breaking one guarantee of this branch (an altered worked example, a wrong weekday in one,
  the theme not stored, dark by default, a second cobalt button, labels beside fields, the status chip without its
  icon, the How example left out, a guide section over 150 words, the theme stored under another key, a color written
  outside `tokens.css`, the removal error without its field's name): each made its test fail. Dark by default first
  passed, because its test switched the theme itself; the test now checks the page as it opens.
- Screenshots in light and dark, at 1280 and 375 px wide, with a result, both notices, a day of one's own, an error
  and the guide: looked at, not committed.

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
- 2026-11-16: the app reflects the whole foundation, rebuilt on the web starter; the starter's downloads approved
  (a Node base image, the npm packages from `npm ci`, the PyPI lookups and installs for the fully pinned Python list).

## Last session (2026-11-15 and 2026-11-16)

Done: pull requests #18 to #20 merged; the app run in Docker for review; the foundation audit; this branch's
work and its checks above.
Half-done: this branch's pull request.
