---
name: close-session
description: End-of-session routine, run only with /close-session. Rewrites STATE.md, saves what the session taught to the owner's memory (the /reflect step) and proposes rules learned, checks for secrets, commits the named files on the open work's feature branch and pushes that branch, then reports. Does not merge (the merge follows the review, CLAUDE.md › Where the agent stops).
disable-model-invocation: true
---

# Close session

This repository is public: everything written here is published. STATE.md holds the technical state only; the
owner's words, approvals and private notes are kept outside this repository.

1. Find the repo root: `git rev-parse --show-toplevel`.
2. Rewrite `STATE.md` at the repo root (create it on the first close). It is a snapshot, not a log: replace it, do not
   append. It holds: where the work stands now (branch, what is built, what is next); decisions made today, each with
   its date; pending items (done ones removed, new ones added); and the last session: its date, what was done, what
   is half-done and what was learned. Be plain and honest: half-done work is called half-done.
3. Memory and rules learned. This routine also does the /reflect step, so one routine closes the session. Read
   `~/.claude/skills/reflect/SKILL.md` and apply its source-of-truth gate, tiers, rules and memory format to this
   session. Tier 1 items go to the owner's memory folder, never into this repository:
   `~/.claude/projects/<slug>/memory/` and its `MEMORY.md`, where the slug is the repo root's absolute path with every `/` and `.` replaced by `-`; create
   the folder if it does not exist yet. `STATE.md` is a snapshot the next close replaces, so what step 2 wrote there
   does not count as already recorded. Rules learned are Tier 2: if the same correction was needed twice today, or a
   bug was fixed that could come back, propose it to the owner as a line for CLAUDE.md, a Known traps entry, or a
   guardian (CLAUDE.md › Guardians; a guardian belongs in the pull request of its fix). Do not write it until the
   owner approves. If `~/.claude/skills/reflect/SKILL.md` does not exist (a cloud session, or a machine without the
   owner's setup), say so and skip the memory saves; still propose the rules.
4. Secrets check, without printing any secret: for each changed or new file (`git status --porcelain
   --untracked-files=all`) and each file in the commits a push would send (`git diff --name-only <upstream, or
   main>...HEAD`), report by file and line only, never the matched text, anything that looks like a secret: `.env`
   files, keys, tokens, passwords, `*.pem`, connection strings. If anything is found, stop and tell the owner before
   anything else.
5. Commit, push and report. Stage the named files and commit them on the open work's feature branch, so the records
   go into that work's pull request (CLAUDE.md › Rules: no records-only rounds), and push that branch, never `main`.
   The pull request's one publication check (CLAUDE.md › Publication check) runs before its first push; content
   changed after it leaves without a second check, each change logged in the work log. Then report, opening with one
   line: `Needed from you: nothing` or `Needed from you: <one thing>`. Then:
   - the current branch, and whether it is ahead of or behind its upstream. If it is `main`, create a feature branch
     (`git switch -c <short-name>`) before anything is staged, and say so;
   - every changed or new file, by name, with one line on why it changed. A file the session created or changed that
     `git status` does not list is ignored: check it with `git check-ignore -v <file>` and name the rule;
   - the staging command used, with named files only; `git add -f` only for a file the owner means to commit that a
     tooling-folder rule (such as `.claude/`) hides, never for one a secrets rule hides;
   - the commit message used;
   - the memory step's report (step 3), in the sections /reflect's report uses, or why it was skipped;
   - the publication check's verdict, PASS or its numbered findings, and how each was fixed: a wording finding once,
     without a rerun, the choice and its reason in the work log; one under its items 1 to 5 before the push, named
     here (CLAUDE.md › Publication check);
   - three closing lines: Not done, Not verified, Decided alone, each "none" when empty, never dropped.
   The merge comes later, after the checks and the separate review (CLAUDE.md › Where the agent stops), not in this
   routine.

Never run `git add -A` or `git add .`, never push to `main`, never merge from this routine, never use --force.
