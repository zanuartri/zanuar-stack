---
name: test-first
description: Fix a bug by writing a focused failing test first, then making it pass. Use when asked for TDD, a regression test or a failing test, or when the bug has an obvious cheap test target. Skip when the test path is unclear, slow or integration-heavy.
---

# Test first

Make the bug executable before touching production code.

1. **Pin the bug**: expected behaviour, actual behaviour, the code path, the smallest repro.
2. **Pick the nearest existing test style** for that path (unit, component, integration). No obvious cheap path? Don't build a harness from scratch; skip to the fallback.
3. **Write one small test** that would have caught it. It asserts intended behaviour, not current internals.
4. **Run it and watch it fail for the right reason.** Wrong reason, or it passes? Fix the test first.
5. **Fix** with the smallest change that keeps nearby contracts intact.
6. **Run it again**: green. Run the neighbouring tests too.

## Fallback
If a test would need broad fixtures, brittle mocks, slow infra or production state, use the closest executable check instead (a script, a repro command, a log assertion). No test beats a bad test.

## Guardrails
- Never change a test to match a wrong implementation, or weaken an assertion without a stated reason.
- Flaky bug: make the test deterministic and say what signal it locks down.

## Report
The failing-before evidence, the passing-after run, and anything else you ran. If you couldn't show a failure first, say why.
