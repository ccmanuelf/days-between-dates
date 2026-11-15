---
name: open-session
description: Start-of-session routine. Use when the owner says "abro", "retomamos" or "open session". Reads the app's state notes and git status, reports where the work stands and proposes the next step. Changes no file in the working tree; git fetch updates .git.
disallowed-tools: Edit, Write, NotebookEdit
---

# Open session

1. Find the repo root: `git rev-parse --show-toplevel`.
2. Read `STATE.md` at the repo root: where the work stopped, open decisions, pending items, the last session. If it
   does not exist, say so. If the owner's memory index (`MEMORY.md`, loaded when the session starts) is in context,
   also take the lines marked ⏳ or ON RESUME: what they hold counts as pending.
3. Read the repo's state. These commands change no file in the working tree; `git fetch` writes inside `.git` (the
   fetched objects, the remote-tracking references and `FETCH_HEAD`):
   git fetch origin --quiet
   git status --short
   git log --oneline -5
   git rev-list --left-right --count @{u}...HEAD   (behind / ahead; skip if there is no upstream)
4. Report in 4 to 6 lines. The first line says what is needed from the owner: nothing, or the one thing. Then: where
   the work stopped, open decisions, the most important pending items, any uncommitted changes, and any difference
   with the remote. If STATE.md and git disagree, say so instead of picking one.
5. End by proposing one concrete next step.

Do not edit files, write code, stage or commit anything until the owner says what to do.
