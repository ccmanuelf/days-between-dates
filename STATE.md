# State

Updated 2026-11-15. A snapshot, replaced at each close (close-session); the history is in git.

## Where the work stands

- `main`: pull request #17 merged (the years accepted, 1950 to 2150).
- Branch `docker-required-check`, for one pull request, on the owner's word of 2026-11-15: the `docker` CI job is a
  required check on `main`, with `test`; `CLAUDE.md` says so, and adds the owner's rule to leave nothing that slowly
  eats space (CI artifacts and caches, local Docker leftovers).
- Next, on the owner's word of the same day: the page restyled to `DESIGN.md` (layout, typography, spacing and
  states, light and dark, accessibility) and a visible user guide in the app, one section per feature with examples
  from the known answers, in English and Spanish; a pull request of its own.

## Checked on this branch (2026-11-15)

- Branch protection on `main`, read in full before and after the change: required checks `test` and `docker`
  (GitHub Actions), not strict; each other protection setting equal in the two reads.
- CI: `ci.yml` has no artifact upload and no cache step; the GitHub API lists 0 Actions caches and 0 artifacts.
- Local Docker, this project only: its stopped container, its image and eleven build-cache records removed (the
  `Dockerfile`'s steps, and the `python:3.13-slim` base, on which, in the build cache's parent links, no other build
  sat); the `days-between-dates_app-data` volume kept. The one untagged image on the machine runs `sh` and dates from
  2026-10-27: not an earlier build of this app.

## Pending

- Before the first release: the README gains *Proven work* (`CLAUDE.md`, *Proven work*).
- An intermittent failure seen once on 2026-11-14 in
  `test_e3_a_storage_failure_on_an_edit_takes_the_count_off_the_screen[add-unwritable]`; its cause is not
  established.
- `python -m pip install` is not covered by the ask rules (the template has the `python3` form only).
- `DESIGN.md` restates values from `style.css` and `tokens.css`. No test reads `DESIGN.md` (searched `tests/` and
  `scripts/`), so its copies can drift from those files.

## Decisions (2026-11-15, the owner's)

- After `/security-audit`: merge pull request #14, then fix the audit's top four findings and the review's three
  minor findings in one follow-up pull request (#15, merged).
- The working rules now in `CLAUDE.md`, effective 2026-11-15.
- Docker only, with no public demo or external host; the passing Docker check is the deployment validation (SPEC,
  *Approval*, 2026-11-15).
- The years accepted: 1950 to 2150 (SPEC, *Approval*, 2026-11-15).
- The `docker` job a required check; nothing left that slowly eats space; the restyle and the user guide. For the
  guide's length, the owner's goal: a guide no more elaborate or complicated than the app and its features; the
  SPEC change it needs goes with that pull request.

## Last session (2026-11-14 and 2026-11-15)

Done: pull requests #13 to #17 merged; `/security-audit` run; the docker check made required; this branch's work.
Half-done: this branch's pull request; the restyle and the guide.
