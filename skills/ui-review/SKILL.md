---
name: ui-review
description: Review a PR's user-facing UI against its design handoff using screenshots and return PASS or FIX.
---

# UI review

The manager requests this review only when the ticket changes user-facing UI and a design reviewer is available. Code review still runs separately.

1. Get the PR and its [design handoff](../design-handoff/SKILL.md). Use screenshots from the PR or capture them with the repo's [make-verify](../make-verify/SKILL.md) recipe. Check that the proof matches the PR revision and covers the required screens, states, and viewport sizes.
2. Compare the proof with each acceptance check. Run the stated steps for checks that need interaction. Ask for any proof you cannot get from the PR or recipe.
3. Return **PASS** when the evidence supports every check. Otherwise return **FIX**. For each finding, give the screen, state, viewport, expected result, actual result or missing proof, and a link to the evidence when available.
