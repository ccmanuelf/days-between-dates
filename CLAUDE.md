# Days between dates — working context

This repository is public. Everything committed here is published.

## What this app does

A small web app that counts the days between two dates: total days and business days, under both conventions side by
side (the start date not counted · both dates counted). Business days are Monday to Friday minus the active
calendar's holidays: Mexico's mandatory rest days under the federal labour law, or the United States' federal legal
public holidays with their observed days. The user keeps holidays of their own, one list per calendar, in SQLite.
Every convention shows on screen, and every count is checked against a known answer that carries its source. It is
didactic: for a practitioner who lives in spreadsheets and is learning to build a tested tool instead of a formula.
`SPEC.md` is the approved specification: its scenarios, acceptance criteria AC1–AC18 and known answers K1–K11 are the
contract. It is not changed without the owner's approval.

## Definition of done

Functional, does not crash, does not lie. "Lying" means: frontend features never connected to the backend; backend
code that is never called; schemas partially built; tests that check that something exists instead of what it does;
tests of code that is not wired to anything. For calculations, rules and definitions, the result is confirmed against
the known answer every time, not once.

A task is done only when all of these are true:

- Every acceptance criterion in `SPEC.md` passes, the scenarios run without crashing, and the Docker check passes:
  it is the deployment validation; there is no public demo and no external host.
- Each criterion is verified through the real wiring: page → API → SQLite → back, on the running server. Every UI
  action reaches that path, the path runs, and it returns real data.
- No orphans: every UI control reaches a backend path that executes; every endpoint has a caller, or it is removed;
  every schema object is written and read. An orphan is a defect, not partial progress.
- No half-built schemas, stubs or placeholder data left behind. Design tokens are the one exception, on the owner's
  decision of 2026-11-14 (`JUDGMENT.md`): `app/static/tokens.css` may define a token before any rule reads it, and
  `DESIGN.md` names the tokens no rule reads yet.
- Tests fail on the broken version and pass on the fixed one; a test that accepts two different answers defends
  neither.
- The known-answer checks run on every pull request and every push to `main`, against reference values that carry a
  source.
- Checks are green.
- Done is shown with evidence (test output, the orphan list, the Docker check), never asserted.

If any item above was not done, the task is not done, and saying it is done is the failure.

## Where the agent stops

- The agent's work ends at: pull request open, checks green, and one separate review, by a pass that did not do the
  work, run and answered. Claude Code then merges it (below).
- The separate review is the reviewer agent in `.claude/agents/reviewer.md`, run as its own subagent, never as a fork
  (a fork inherits this conversation). It returns its findings and `"passed"`, true or false. A pass that returns
  FAIL for missing inputs is not the review pass: the session supplies them and runs it.
- One review pass and one publication check per pull request. A finding about wording only is fixed once, without a
  rerun. Any other finding is fixed, with a test when it is about behaviour, and the checks rerun; the review is not
  run again.
- The agent carries the agreed plan to the end without stopping: commit, push, pull request, CI, merge, and the merged
  branch deleted. It stops and asks the owner only for a scope change, a new product decision, or an irreversible step
  outside the plan, and where another line of this file says to ask (an ambiguous SPEC, a gate set aside, a command
  denied twice, a change to CI, the security audit before a release). A failed CI test it fixes itself, and asks only
  if the fix changes behaviour the owner agreed.
- A command denied by a permission check is retried once, as one plain command with no pipe or chain; denied again,
  the agent asks the owner.
- The agent never pushes to `main` and never runs `git add -A`. It stages named files only.
- Claude Code merges work the owner agreed (the owner approves the plan once), after the checks are green and the
  separate review's findings are fixed. No other agent merges, and nothing the owner has not agreed is merged. It
  merges with `gh pr merge <n> --repo ccmanuelf/days-between-dates --merge --delete-branch --match-head-commit
  <checked head>`, so a branch that moved after its last green checks is not merged, and `--body` set to the pull
  request's title, a blank line and the `Co-Authored-By:` trailer its commits carry, so its merges stand apart from
  the owner's. Then it reads the merge back: the merge commit with its trailer, and `main` matching the merged
  branch. Once the read-back passes, and only with a clean working tree, it switches to `main`, runs
  `git fetch --prune` and `git merge --ff-only origin/main`, and deletes the merged local branch with
  `git branch -d`, never `-D`.
- The agent never suggests a `!` command for anything a rule or deny rule blocks: a `!` command runs past the deny
  rules.
- Once before each release (not every push), the agent asks the owner to run `/security-audit`, the read-only audit
  of the whole app, and releases nothing until its report has gone to the owner.

## Rules

- Work on feature branches. `main` changes only through a pull request with passing checks.
- No secrets, no credentials, no third-party confidential material.
- When the SPEC is ambiguous, ask. Do not fill the gap with an assumption.
- If a rule in this file clashes with what the owner asks, say so, quoting the rule (file and line), and decide
  together before acting on that part; a silent override, either way, is the failure. A rule under *Where the agent
  stops* is not crossed until this file is changed on the owner's word.
- The owner's instruction decides what is done, not what is reported as true. A gate (an approval, the SPEC, an
  acceptance criterion, a known answer) is set aside only when the owner names it and its scope, or picks the option
  that says so; experience, insistence or a typed answer that neither names the gate nor picks that option does not.
  Otherwise ask once, in one line, quoting the words that would set it aside, and wait; once the owner says them,
  restate the exemption in one line before acting. Change a stated assessment only for a new fact or argument, and
  name it; insistence alone is neither.
- Scope changes go back to the SPEC and its approval.
- A holiday rule carries its primary source and the date it was checked; a value without a source does not ship.
- A string shown on the page exists in English and in Spanish; a missing one fails a test, never falls back silently.
- Wording, documentation sentences, records and minor gate findings are the agent's to settle: it picks the most
  accurate, shortest wording, writes the choice and its reason in the work log (the session's decisions file, kept
  outside this repository), and keeps going. It never asks the owner how a sentence should read.
- No records-only rounds: records (`STATE.md`, `JUDGMENT.md`, the docs) go in the same pull request as the work.
- A session starts with the open-session skill and ends with the close-session skill, whose records go into the
  open work's pull request.
- When a fixed bug is a repeatable pattern, add a lint rule if one exists, otherwise a guardian test with a fixture
  it must catch. *Guardians*, below, governs both: a pattern counts only when all three of its conditions hold, and
  every guardian, a lint rule included, has its fixture and its proof.
- The `rtk` ask rules in `.claude/settings.json` match commands the rtk hook rewrites; without rtk they never match.

## Publication check

This repository is public, so a push, a commit message, a branch name, pull-request text, release notes and deploy
settings are all publication. Once per pull request (*Where the agent stops*), before its first push, a pass that did
not write the content, the reviewer agent, checks it for:

1. Names of people, companies or clients that are not already public in this repository.
2. Numbers or data whose source is not public.
3. Content copied or derived from documents that are not public. Software the owner has recorded in writing as his
   own is not such a document; employer or client data inside it, and an employer's or a client's documents, always
   are.
4. Infrastructure details: private hosts and internal addresses, and environment-variable values; a variable's name
   is fine unless it reveals private infrastructure.
5. Anything that identifies a person or an organisation by implication.

It also checks every "only", "none", "nothing", "all" or "never" used as a claim in that content's prose (README and
other docs, comments, commit messages, pull-request text): each names what was searched or counted, and where, or its
sentence narrows itself ("in X", "as far as Y showed"); one that does neither is a finding.

The result is PASS, or numbered findings, each with a proposed fix. The agent fixes each finding: one about wording
once, without a rerun, with the choice and its reason in the work log; one that would publish something under items 1
to 5, before anything leaves the machine, named in its report. Content changed after the check, by those fixes or
later in the pull request, leaves without a second check, each change logged in the work log. When unsure, the check
fails. After anything is posted, read back what was posted and compare it with what was checked and the logged
changes.

The README's *Proven work* section (below) gets this check and the extra checks listed there.

## Guardians

A guardian is a test that watches the whole codebase, not one function. It fails when a mistake that already caused a
bug is written again anywhere, by an agent or by a person. A fix removes a bug once; a guardian keeps the pattern from
coming back. It does not replace the fix's own test, which shows the behaviour through the real wiring.

Write a guardian when all three are true:
- The mistake is a pattern that can be written again elsewhere, not a one-off slip.
- The wrong version looks reasonable, so it will be written again without doubt.
- It can be detected by reading the code (text, imports, structure) without running the app.
Otherwise, the fix and its normal test are enough.

How:
- Prefer a rule in a free Python linter when it can express the pattern; use a scan test in pytest when it cannot.
  Either way it runs in the check command, so CI enforces it, and it is never skipped or deselected. No paid
  services. Adding a linter to the check command changes CI: ask the owner first.
- Every guardian has:
  1. A name that states the rule in plain, positive words, under `tests/guardians/`.
  2. A scan of all source files that reports each hit with file, line, and what to use instead.
  3. An explicit list of allowed exceptions, each with its reason. No exception without a reason.
  4. A self-check: a fixture file under `tests/fixtures/` that contains the bad pattern on purpose. The guardian must
     flag it; if it stops flagging it, the guardian fails. Fixtures are excluded from the main scan.
  5. Proof in the pull request: red on the code before the fix, flagging the fixture, and green on the fixed code.
  6. An entry under *Known traps*.
- When a bug fix meets the three conditions above, the guardian goes in the same pull request as the fix. Do not add
  guardians outside the task's scope.

## Judgment log

`JUDGMENT.md` records what reviews changed. An entry is written only when a review changes something, in the same
commit as the change, and never for a trivial fix. The file is created with its first entry. Each entry:

- **<date> — <the change, in a few words>** (<commit or pull request>)
  - Produced: what the AI produced.
  - Wrong: what was wrong with it.
  - Caught by: who or what flagged it, credited by role (the owner, the reviewer agent, a named test or check, CI),
    or by a name already public in this repository (*Publication check*, item 1).
  - Decision: the owner's decision, in the words the owner gives for this file; for a finding the agent settled
    itself (*Rules*), "settled by the agent" and the reason.

`JUDGMENT.md` is published like everything else here, so its entries pass the publication check. The owner's other
words, approvals and notes stay outside this repository (close-session).

## Proven work

Before the app's first release, the README gains a section called "Proven work", kept current
after. In this order:

1. Problem: who has it, and what it costs them: a number only if it was measured, with its source; otherwise in words.
2. What I built: screenshots, with made-up data only.
3. How: stage by stage, what AI did and what the owner did.
4. Top 3 corrections, taken from `JUDGMENT.md`: fewer if it has fewer, or "no review changed anything".
5. Result: only what was checked; anything else says "not measured".
6. What I'd do differently.
7. Where it applies.

Claude Code drafts it, marking each part the owner writes `[OWNER: …]`. Those parts are the owner's account, not
wording: *Rules* (wording settled by the agent) does not cover them. The draft is not committed while a marker
remains: every pushed commit is published, its history included. A session without the owner leaves the draft
uncommitted and names it in its close-session list.

Its publication check (*Publication check*, above, run by the reviewer agent) also fails on:
- an `[OWNER:` marker left;
- a number that was not measured;
- the phrase "AI expert", in any spelling;
- any employer's names or data; people appear as roles, also in corrections copied from `JUDGMENT.md`;
- a screenshot showing real data, a private host or address, a user name or a local path: each image is opened and
  looked at.

## Stack

Python and FastAPI, SQLite, one HTML page with a JavaScript module calling the JSON API; tests with pytest and
Playwright for Python. Plain CSS, no build step; the look and its tokens are in `DESIGN.md`. Delivery rung 1: user
space, no admin. The SQLite file is created at run time, at `DBD_DB_PATH` (default `data/app.db`), and never
committed. A request addressed to a host name other than `127.0.0.1`, `localhost` or one listed in
`DBD_ALLOWED_HOSTS` is refused; a write with a body (adding a holiday, storing the language) must be sent as
`application/json`, at most 4096 bytes. Docker:
`Dockerfile` and `compose.yaml` run the app with its database in a named volume. Deployment: Docker only; the passing
Docker check is the deployment validation, with no public demo and no external host (the owner, 2026-11-15).
Licence: MIT. Interface: English and Spanish.

## Commands

```
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
python -m playwright install chromium
python -m uvicorn app.main:app        # http://127.0.0.1:8000
python -m pytest -v
docker compose up --build             # the same app in Docker, http://127.0.0.1:8000
```

`CHROMIUM_PATH`, if set, points the browser tests to a Chromium already installed.

CI: `.github/workflows/ci.yml` runs `python -m pytest -v`, the known-answer checks among them, on every pull request
and every push to `main`; the branch rule on `main` requires its `test` check. Its `docker` job, the deployment
validation, builds and starts the app with compose and checks it with `scripts/docker_check.py`, the volume included;
it is not a required check.
Changing the workflow changes CI: ask the owner first.

## Known traps

One entry per guardian: what goes wrong, why, the correct pattern, and the guardian's name.

- **A write that reads its own body.** What goes wrong: a route reads its body with `request.json()`, `.body()`,
  `.form()` or `.stream()` outside `json_body`, a Pydantic model, or FastAPI's `Body`, `Form`, `File` or
  `UploadFile`. Why: that skips `json_body`'s checks, so a body over 4096 bytes is read whole. `request.json()`,
  `.body()` and `.stream()` also read a `text/plain` body, which a page on another site can make a browser send
  without asking the server; `.form()`, `Form`, `File` and `UploadFile` read form bodies, which a browser sends the
  same way. Tried on 2026-11-15 (FastAPI 0.162.0): a `Body()` parameter typed `str`, `bytes` or `Any`, and a
  `RootModel[str]`, accepted a `text/plain` body; whether a parameter refuses one depends on its type. Correct
  pattern: `body = await json_body(request)` (`app/main.py`). Guardian:
  `tests/guardians/test_every_write_reads_its_body_through_json_body.py`. It does not see a route parameter typed
  `dict`, which needs none of those imports: FastAPI reads that body itself, and took a JSON body over 4096 bytes
  when tried on 2026-11-15. Take the body with `json_body`, not as a typed parameter.
