---
name: interview
description: Interview the owner one question at a time until goal, scope, acceptance and non-goals are unambiguous, then summarise back for confirmation. Use for a new feature request to the orchestrator or when the owner says interview or "ask me first".
---

# Interview

Nothing gets planned until you and the owner agree on what "done" means.

Who runs it: the orchestrator when one is running (once, at product level); the manager only when the owner talks to it directly with no orchestrator.

## How to ask
- **One question per ask.** Wait for the answer before the next one.
- Multiple choice, 2–4 options, your **recommended option first**, labelled `(Recommended)`, with one line on why. The owner can always answer in their own words.
- Each question stands alone: state the context and the trade-off, not just "A or B?".
- **Always use the harness's interactive question tool**, so the owner answers with one click:

  | where you run | tool |
  |---|---|
  | Claude Code | `AskUserQuestion` |
  | Codex and other harnesses | that harness's built-in question/ask tool |
  | Orca bot | `orca bot item set <n> --status needs-you --comment "<context>" --ask "<question>?" --option "<label> \| <detail>" … --recommended <n>` |
  | Orca worker | `orca orchestration ask --from <your session> --question "…"` (put the options in the question) |

  Fall back to a short numbered list in chat only when the harness has no such tool.

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
