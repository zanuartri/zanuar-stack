---
name: big-plan
description: Design the workflow itself before writing code for large, ambiguous or long unattended work (migrations, multi-part features, anything reviewed after the owner steps away). Use when the owner says big plan, "figure it out", or no narrower skill fits.
---

# Big plan

For big work, the first deliverable is the plan of phases, not code.

## 1. Frame
Write down, before starting:
- **Done** as a check that can fail (a command, a number, a diff).
- **Size**: rough units of work and the blockers you already see.
- **Rigor**: more gates for one-way doors and wide blast radius, fewer for cheap reversible steps.

Show this to the owner once before a long run. Reversible steps don't wait for approval.

## 2. Design the phases
- Split into units that can land on their own. Riskiest unknown first.
- Build the check before the change, and capture the baseline so results read "before vs after".
- One-way-door design choices get **shape-first**; mechanical work doesn't.
- Fan out only across clean seams, one worktree per worker (one ticket each).
- Write the phase list down. That list is what the owner reviews.

## 3. Run each unit as an experiment
Hypothesis, smallest change, measure on the real artifact, keep or revert. Verify each unit before the next. Trust artifacts, not self-reports; a suspiciously easy pass means check the measurement. Verdicts are VERIFIED, NOT VERIFIED or INCONCLUSIVE, and inconclusive is not a pass.

## 4. Leave a trail
Log forks, results and reverts with **decision-log** as you go, not at the end.

## 5. Hand back
Check the whole against the step-1 definition of done on the real product. Turn any repeated correction into a lint rule, test or script.
