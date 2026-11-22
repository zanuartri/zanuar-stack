---
name: root-cause
description: When debugging, trace a symptom back to the first place the system went wrong and fix it there, not where it surfaced. Use for any bug, failing check, or when the owner says root cause or "fix it properly".
---

# Root cause

The root cause is the first point where the code did something it shouldn't, or failed to handle a state it should.

- **Reproduce first.** Then keep asking "why" until the answer is a wrong decision in the code. Stuck? Add logging and read the real state instead of guessing.
- **Is the triggering state legitimate?**
  - Yes: handle it where the code broke.
  - No: a guard there hides the bug. Find what produced the state. Guards, retries, swallowed errors, clamped values and dropped data are the usual hiding places.
- **Fix the pattern, not the instance.** Grep for every other place with the same fault, and every caller of the function you change.
- **If it took a deep dig**, propose one cheap always-on signal (a log line, an assert, a metric) that would have shown it immediately.

Report: symptom, root cause (`file:line`), fix, and the siblings you checked.
