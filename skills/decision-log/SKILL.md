---
name: decision-log
description: Keep a reviewable trail of decisions for long or unattended work, one row per decision (what, why, evidence, result), in the ticket db or a TSV. Use for multi-phase runs, big-plan work, or when the owner says log your decisions or show your work.
---

# Decision log

One log, one row per decision. Short cells, evidence as a pointer.

## Columns
`ts` · `phase` · `decision` (one line) · `why` (plain words) · `evidence` (commit SHA, PR, `file:line`, artifact path, never prose) · `result` (`tests green`, `reverted`, `INCONCLUSIVE`, `open`…)

## Where
- **db** (default when the team db exists): the `decisions` table, with `ticket` set. Insert with stdlib `sqlite3`, passing values as parameters.
- **TSV**: `decisions.tsv` in the work dir, or `.audit/<slug>.tsv` when several efforts run. Header row first. Strip tabs and newlines from cells; prefix cells starting with `= + - @` with `'` so spreadsheets don't run them.

Keep it out of git unless the reviewer needs the trail to trust the result; then commit it with the PR.

## What earns a row
A fork taken, a unit finished with its verify result, a revert and its trigger, a blocker, a gate fixed. One row per loop iteration. Not every command.

Write rows the way you'd tell a teammate: concrete, plain, no jargon.

## Several runs, one log
When you start writing into a log that already has rows, first read the last rows. Your first row has phase `start` and names the rows before it you didn't write and who you are (agent/session id). Use `start` for nothing else.
