---
name: interview
description: Before starting any feature or non-trivial change, interview the owner one question at a time until goal, scope, acceptance and non-goals are unambiguous, then summarise back for confirmation. Use on every new feature request to the lead, or when the owner says interview, grill me, or "ask me first".
---

# Interview

Nothing gets planned until you and the owner agree on what "done" means.

## How to ask
- **One question per message.** Wait for the answer before the next one.
- Multiple choice, 2–4 options, your **recommended option first** with one line on why. The owner can always answer in their own words.
- Each question stands alone: state the context and the trade-off, not just "A or B?".
- Use the harness's question tool if it has one; otherwise a short numbered list. (Orca workers: `orca orchestration ask`.)

## What to settle, in order
1. **Goal**: the problem and who it's for.
2. **Scope**: which repos and areas change.
3. **Acceptance**: observable checks that prove it works.
4. **Non-goals**: what is deliberately left out.
5. Whatever those answers open up (contract shape, rollout, data migration…).

## Facts are yours
Anything the code, docs or tools can answer, look up yourself. Ask the owner only for decisions.

## When to stop
Stop when an answer would no longer change the plan. Then post a compact summary (goal, scope, acceptance, non-goals, decisions) and ask one last question: "Is this right?" Act only after a yes.
