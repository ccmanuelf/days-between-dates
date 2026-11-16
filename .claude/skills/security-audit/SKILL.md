---
name: security-audit
description: Read-only security audit of the whole app, run only with /security-audit, which the owner types, once before each release. Checks input validation, injection and secrets always, and IDOR, auth and roles, tokens and links, rate limits and headers when the app has logins. Reports a table per area and the top 5 fixes, and flags overlap with /security-review. Changes no file.
disable-model-invocation: true
disallowed-tools: Edit, Write, NotebookEdit, Bash, WebFetch, WebSearch
---

# Security audit

Read-only: while it runs, `disallowed-tools` removes the six built-in tools it names (Edit, Write, NotebookEdit, Bash,
WebFetch, WebSearch). Tools from MCP servers, and the Agent tool, are not on that list: do not call one that writes
files, runs processes or reaches the network. The list does not enforce this line; it is an instruction. It reads
the whole app, not only a diff, and starts no server.

Run it once before each release (`CLAUDE.md`, *Where the agent stops*). Not before every push, although every push
to this public repository is publication (*Publication check* in `CLAUDE.md`).

## 1. Areas

Always:
- **Input validation**: every value from outside (request bodies, query strings, path parameters, form fields,
  uploaded files) is checked for type, range and size on the server before it is used, not only in the page.
- **Injection**: SQL built from strings, shell commands or file paths built from outside values, HTML inserted
  without escaping (`v-html`, `innerHTML`), and outside values run as code (`eval`, `new Function`).
- **Secrets**: keys, tokens and passwords in tracked files, in logs or in what the page receives; `.env` kept out of
  git.

Only when the app has logins (its SPEC says so, or the code has sign-in); otherwise list each as "not applicable: no
logins", saying where that was checked:
- **IDOR**: a record read or changed by an id from the request without a check that it belongs to the caller.
- **Auth and roles**: every route that needs a login, and every role check, is enforced on the server.
- **Tokens and links**: tokens and one-time links expire, cannot be guessed, are checked on use and never logged.
- **Rate limits and headers**: sign-in and other costly routes are rate limited; the security headers are set
  (Content-Security-Policy, X-Frame-Options or frame-ancestors, X-Content-Type-Options, and HSTS where the app is
  served over HTTPS).

## 2. Report

One table per area:

| severity | file:line | what happens | how to fix |
|---|---|---|---|

Severity: **high**, exploitable as the app runs; **medium**, exploitable under a condition the row names; **low**,
hardening. A row without a file and line is not a finding. An area with nothing found says "none found" and what was
read.

Then **Top 5 fixes**, most severe first, one line each.

Then **Overlap with /security-review**: `/security-review` reads the branch's changes, and the reviewer agent
(`.claude/agents/reviewer.md`) reads the changed files; this audit reads the whole app. If `/security-review` ran
earlier in this session, mark each finding it also reported. Otherwise write "/security-review: not run in this
session".

## 3. Stop

The audit fixes nothing. Its report goes to the owner, who decides what is fixed before the publish.
