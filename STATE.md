# State

Updated 2026-11-15. A snapshot, replaced at each close (close-session); the history is in git.

## Where the work stands

- `main`: pull request #18 merged (the `docker` CI job a required check, with `test`; the rule to leave nothing that
  slowly eats space).
- Branch `restyle-guide`, for one pull request, on the owner's word of 2026-11-15: the page restyled to `DESIGN.md`
  (cards, a type and spacing scale, buttons and fields with hover, focus, press and invalid states, light and dark),
  and Help made a user guide at the top of the page: an introduction, its contents, and one section per feature, four
  of them with worked examples from the known answers (K1, K3, K9a, K10, K4), the first also with the dates accepted,
  in English and Spanish, each section at most 150 words. SPEC S15 and AC17 follow the owner's request and answer,
  quoted in *Approval*; the ceiling, S15's introduction, contents and dates, and S13's and AC15's light clause
  narrowed to the four color tokens are the agent's reading, marked 【C】. A refused date marks the field it was typed
  into, and each message shows where it belongs. A guardian keeps colors the contrast check cannot read out of the
  stylesheets. `JUDGMENT.md` gains the entry pull request #18's review called for.

## Checked on this branch (2026-11-15)

- The full suite on this machine: 213 passed. On `main`, CI's run 43801865608 (pull request #18's last head, whose
  tree `main` has): 202 passed.
- Before the change, 15 of the new and changed tests failed on `main`'s code; the in-view test, which `main` already
  met, passed there and failed under mutation R9. The K10 test, under its final name, fails on `main`'s code. After
  the review, its five new or changed page tests (a failed removal, a language not stored, the guide's `h2`
  headings) failed before their fix.
- The color guardian: red on `style.css` with the `color-mix()` hover put back, all seven fixture lines flagged,
  green on this code.
- Nine mutations, each breaking one guarantee of this branch (K10's own day, the last date accepted, the
  invalid mark, where the error shows, a section over 150 words, the weekday's form, a hidden example, a hover
  color the contrast check cannot read, Help moved below the page): each made its test fail.
- Screenshots in light and dark, at 1280 and 375 px wide, in English and Spanish, with a result, both notices, a
  day of one's own, the guide open and an error: looked at, not committed.

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
- The `docker` job a required check, and nothing left that slowly eats space (#18, merged).
- The restyle and the user guide; the guide no more elaborate than the app (SPEC, *Approval*, 2026-11-15).

## Last session (2026-11-14 and 2026-11-15)

Done: pull requests #13 to #18 merged; `/security-audit` run; this branch's work and its checks above.
Half-done: this branch's pull request.
