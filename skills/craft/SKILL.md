---
name: craft
description: Debug at the root cause, simplify before adding, write focused regression tests, and sweep comments. Use for bugs, additions, refactors, TDD or comment cleanup.
---

# Craft

## Root cause

Reproduce the failure and trace it to the first wrong decision. Inspect real state when the path is unclear. Handle valid input where handling failed. Trace invalid input back to its producer. Check callers and other instances of the same fault. Report the symptom, cause, fix and related paths checked. For hard-to-diagnose failures, suggest a cheap signal that would have exposed the cause.

## Cut first

Remove dead code, flags, validation, stale references and repeated instructions before building. Check usage before cutting and preserve supported behavior. Record meaningful removals in the acceptance checks.

## Test first

When a cheap regression test fits, write it against intended behavior using the nearest existing test style. Run it and confirm it fails for the expected reason. Make the smallest fix, then rerun it and nearby tests. If a test needs a new harness or brittle fixtures, use the closest executable reproduction. Report the before and after evidence.

## Comment sweep

Before handoff, scan the diff for restatements, stale notes, commented-out code and workaround excuses. Delete those and fix the cause within scope. Keep legal headers, public contracts and verified external constraints. Flag uncertain external claims for review. Encode important warnings as types, tests or lint rules where practical. Report remaining issues.
