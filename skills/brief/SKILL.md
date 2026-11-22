---
name: brief
description: Turn a thin task or ticket into a deeper, sharper one (not a bigger one) and rewrite it. Use when writing a ticket or repo brief that feels vague, or when the owner says brief, sharpen, or "make this prompt better".
---

# Brief

Make the task deeper, not wider. Before rewriting it, answer four things:

1. What would a seasoned expert in this area do here that the task doesn't ask for?
2. What raw source would they start from (logs, data, the actual code, the spec) instead of a summary?
3. Which concrete methods and tools would they use?
4. What outside signal, not the agent's own word, would prove the result right? (A test, a benchmark, a diff, a user-visible behaviour.)

Then rewrite the task as a ticket (goal, acceptance, verify, scope) that asks for exactly that.

In the rewrite:
- Choices an experiment can settle: tell the agent to prototype and recommend from what it observed.
- Choices only the owner can make (product, taste, cost): leave them as open questions for the owner, don't guess.
