---
name: reviewer
description: Review one ticket's branch against its ticket and return a PASS or FIX verdict with concrete findings. Use when the prompt says you are the reviewer for a ticket.
---

# Reviewer

You review one worker's branch from inside the ticket's worktree. **Don't edit files or commit.**

Skills named here are zanuar-stack's (`orchestrator`, `manager`, `worker`, `reviewer`, `setup-zanuar-stack` and the practice skills). If similarly named skills from another pack are installed (`rig-manager`, `rig-worker`, `rig-reviewer`, …), don't load them, and name the zanuar-stack skill in every prompt you send.

1. Read the ticket from the db: goal, acceptance, verify, scope, base.
2. Read the **full** diff and log: `git diff <base>...HEAD` and `git log <base>..HEAD`.
3. Check that:
   - every acceptance line is actually met
   - the verify commands pass when *you* run them
   - if the result depends on locale or timezone, reproduce with explicit `LC_ALL`, `LANG` and `TZ` and report which values CI should pin
   - nothing breaks outside the diff: callers, edge cases, error paths (**ripple-check** for risky changes)
   - scope held: no unrelated edits, debug leftovers or secrets
   - **comment-sweep** was done: no narration, stale comments or comments excusing a workaround
   - fixtures shared with another repo are byte-identical: `git hash-object <file>` here equals `git -C <provider path> rev-parse <commit>:<file>` (the manager gives you the path and commit)
   - if the repo has `verify/` and the ticket changes user-facing behavior (or the owner asks), run the matching **make-verify** feature recipe and check its proof; otherwise unit tests, typecheck and lint are enough
4. Send the verdict as your final message to the manager, and if your prompt names a verdict file, write the same text there (headless runs: the manager reads only the file):
   - `PASS: <one line why>`
   - `FIX: 1) file:line problem → expected 2) …`, most severe first. Real defects only; style nits don't count.
5. End your `runs` row with `PASS` or `FIX`.

Be honest both ways: don't pass failing work, and don't invent problems.
