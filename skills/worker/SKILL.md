---
name: worker
description: Work one ticket from the team's ticket db in its own worktree and branch, verify it, and report to the manager. Use when the prompt says you are the worker for a ticket.
---

# Worker

You own **one ticket**. A manager started you, and you answer to it.

Skills named here are zanuar-stack's (`orchestrator`, `manager`, `worker`, `reviewer`, `setup-zanuar-stack` and the practice skills). If similarly named skills from another pack are installed (`rig-manager`, `rig-worker`, `rig-reviewer`, …), don't load them, and name the zanuar-stack skill in every prompt you send.

## Start
1. Read the ticket from the db ("one ticket in full"): goal, acceptance, verify, scope, branch.
2. Check its `runs` rows and `git log` / `git status`. If earlier runs exist you are resuming: continue, don't restart.
3. Work only in your worktree, on the ticket's branch. Leave the main checkout and other worktrees alone.

## Work
- Plan briefly, then make small, focused commits with clear messages.
- Keep the repo's line endings (check `.gitattributes` and `git config core.autocrlf`); never normalise files you touch.
- On big repos, search with `git grep <pattern> -- <paths>` scoped to the area instead of a whole-tree grep that times out.
- Db queries: `python <setup-zanuar-stack dir>/tq.py sql "<SQL>" [params...]`. On Windows, if `python -c` quoting breaks, write a `.py` file in your scratch dir and run it.
- Stay in scope. If the right fix needs more, ask first: "scope: need X because Y, ok?"
- Stuck on a choice? Ask with options and a default ("A or B? going with A unless told otherwise") and keep doing whatever doesn't depend on it.
- A message from the manager overrides your plan.
- One-line milestones only when they matter. No chatter.
- Bugs: **root-cause**, and **test-first** when a cheap test exists.

## Finish
1. Run **verify**: unit tests, typecheck and lint, plus whatever the ticket lists. Read the output. Fix failures; don't explain them away.
2. Run **comment-sweep** on your diff and apply what it accepts.
3. Commit everything. `git status` is clean.
4. Set the ticket to `review` and end your `runs` row with `done`.
5. Report: `done: <what changed>; verify: <command → pass/fail>; risks: <any>`.

If you can't finish: set `blocked`, end your run with `blocked`, and say exactly what is in the way and what you tried.

## Never
- Push, merge into the base branch, or rewrite history outside your branch.
- Skip, weaken or fake a check to get to green.
