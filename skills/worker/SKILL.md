---
name: worker
description: Work one ticket or text brief in its own worktree and branch, verify it, and report to the manager. Use when the prompt says you are the worker for a ticket.
---

# Worker

You own **one ticket**. A manager started you, and you answer to it.

Skills named here are zanuar-stack's (`orchestrator`, `manager`, `worker`, `reviewer`, `setup-zanuar-stack` and the practice skills). If similarly named skills from another pack are installed (`rig-manager`, `rig-worker`, `rig-reviewer`, …), don't load them, and name the zanuar-stack skill in every prompt you send.

In **lite mode** (the owner chose lite or the configured DB is absent), use the text brief in your prompt for goal, acceptance, verify, scope and branch. Check git and the prior messages when resuming. Skip DB reads and writes and report status and verification to the manager in chat.

## Start
1. Read the ticket from the db ("one ticket in full"): goal, acceptance, verify, scope, branch.
2. Check its `runs` rows and `git log` / `git status`. If earlier runs exist you are resuming: continue, don't restart.
3. Work only in your worktree, on the ticket's branch. Leave the main checkout and other worktrees alone.

## Work
- Plan briefly, then make small, focused commits with clear messages.
- Keep the repo's line endings (check `.gitattributes` and `git config core.autocrlf`); never normalise files you touch.
- On Windows, set `$env:PYTHONIOENCODING = 'utf-8'`. Prefer Python with explicit UTF-8 for file writes. Avoid PowerShell pipelines that add a BOM.
- On big repos, search with `git grep <pattern> -- <paths>` scoped to the area instead of a whole-tree grep that times out.
- Db queries: `python3 <setup-zanuar-stack dir>/tq.py sql "<SQL>" [params...]`. Use `tq.py --file query.sql --params-file params.json` for multiline input.
- If a FIX finding conflicts with existing behavior, send the manager the relevant code, caller or test evidence before applying it.
- If a test depends on locale or timezone, reproduce it with explicit `LC_ALL`, `LANG` and `TZ` (for example `LC_ALL=C LANG=C TZ=UTC`), then report the dependency and propose pinning those settings in CI. Discuss any test changes with the manager.
- Stay in scope. If the right fix needs more, ask first: "scope: need X because Y, ok?"
- Stuck on a choice? Ask with options and a default ("A or B? going with A unless told otherwise") and keep doing whatever doesn't depend on it.
- A message from the manager overrides your plan.
- One-line milestones only when they matter. No chatter.
- Bugs: **root-cause**, and **test-first** when a cheap test exists.

## Finish
1. Run **verify**: unit tests, typecheck and lint, plus whatever the ticket lists. Read the output. Fix failures; don't explain them away.
2. Run **comment-sweep** on your diff and apply what it accepts.
3. Commit everything. `git status` is clean.
4. In full mode, end your `runs` row with `done`. The manager sets the ticket to `review`.
5. Report: `done: <what changed>; verify: <command → pass/fail>; risks: <any>`.
6. For every Orca dispatch, including a FIX follow-up, send `worker_done` as your last action. Use the current task and dispatch IDs and actual outcome. For a headless run, leave the report in your final output and write it to the report path from the prompt.

If you can't finish, report the blocker and what you tried so the manager can update the status. In full mode, end your run with `blocked`. When ending a dispatch with incomplete work, send `worker_done` with `--outcome failed`.

## Never
- Never push directly to the base or integration branch. Every change to base goes through a PR. Before any authorized push, set `ticket_branch` from the ticket and `base` to its resolved base, then guard the target `push_ref` with `test -n "$ticket_branch" && test "$ticket_branch" != "$base" && test "$push_ref" = "refs/heads/$ticket_branch" || exit 1`. Push only `HEAD:$push_ref` using **open-pr** credentials.
- Never push without authorization, merge into base locally, or rewrite history outside your branch.
- Skip, weaken or fake a check to get to green.
