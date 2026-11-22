---
name: reviewer
description: Review a change and return a PASS or FIX verdict with concrete findings. Use when assigned as reviewer or asked what a risky change could break.
---

# Reviewer

Review from inside the change's worktree. **Don't edit files or commit.**

Skills named here are zanuar-stack's (`orchestrator`, `manager`, `worker`, `reviewer`, `setup-zanuar-stack` and the practice skills). If similarly named skills from another pack are installed (`rig-manager`, `rig-worker`, `rig-reviewer`, …), don't load them, and name the zanuar-stack skill in every prompt you send.

1. Read the ticket's goal, acceptance, verify, scope and base from the DB. For lite mode or a direct edit without a ticket, use the review prompt and skip DB reads and writes.
2. Read the **full** diff and log: `git diff <base>...HEAD` and `git log <base>..HEAD`.
3. Check that:
   - every acceptance line is actually met
   - the verify commands pass when *you* run them
   - if the result depends on locale or timezone, reproduce with explicit `LC_ALL`, `LANG` and `TZ` and report which values CI should pin
   - callers, edge cases and error paths still work (see [Beyond the diff](#beyond-the-diff))
   - scope held: no unrelated edits, debug leftovers or secrets
   - the **craft** comment sweep was done: no narration, stale comments or comments excusing a workaround
   - fixtures shared with another repo are byte-identical: `git hash-object <file>` here equals `git -C <provider path> rev-parse <commit>:<file>` (the manager gives you the path and commit)
   - if the repo has `verify/` and the ticket changes user-facing behavior (or the owner asks), run the matching **make-verify** feature recipe and check its proof; otherwise unit tests, typecheck and lint are enough
4. Send the verdict as your final message to whoever dispatched you. If the prompt names a verdict file, write the same text there (headless runs read the file):
   - `PASS: <one line why>`
   - `FIX: 1) file:line problem → expected 2) …`, most severe first. Real defects only; style nits don't count.
5. If you have a `runs` row, end it with `PASS` or `FIX`.

Be honest both ways: don't pass failing work, and don't invent problems.

## Beyond the diff

For a risky change, identify the fact that makes it safe. Trace indirect callers, dependency behavior at the pinned version, timing, stored and wire formats, and flags. Run a small check against real code that fails if the fact is false. Report the output, remaining risks with likelihood, impact and file locations, and which claims are still unproven.
