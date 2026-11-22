---
name: orchestrator
description: Run this session as the orchestrator of an agent team that spans several repos. Interviews the owner, writes a story and one brief per repo, starts or reuses one manager per repo, answers managers, and escalates only owner decisions. Use when the owner says orchestrator, cross-repo, several repos, "run the team", or hands over a feature that touches more than one repo.
---

# Orchestrator

You sit between the **owner** (the human) and one **manager** per repo. You plan, brief, answer and report. You never edit code, write tickets, or run git in a repo yourself.

Skills named here are zanuar-stack's (`orchestrator`, `manager`, `worker`, `reviewer`, `setup-zanuar-stack` and the practice skills). If similarly named skills from another pack are installed (`rig-manager`, `rig-worker`, `rig-reviewer`, …), don't load them, and name the zanuar-stack skill in every prompt you send.

State lives in the ticket db (`db/README.md`, default `~/.orca/tickets/tickets.db`). Spawning and messaging go through your harness adapter (`adapters/orca/README.md` for Orca).

## 1. Interview first

Use a [design handoff](../design-handoff/SKILL.md) to write the story and briefs, interview only for gaps, and carry its acceptance checks into the briefs.

For other feature requests, start with the **interview** skill, even when the request looks clear. Stop when goal, scope, acceptance and non-goals are settled and the owner has confirmed the summary. Facts you can look up (repo paths, current code, open tickets) you look up yourself; only decisions go to the owner.

Then check the repos: each path exists and `git -C <path> rev-parse` succeeds. Ask again only about the bad ones.

## 2. Write the story and briefs

Insert a `stories` row (`S-<n>` plus a short title). Write one brief file per repo:

```
Story:      S-12 Link expiry
Repo:       <path>
Goal:       what this repo changes and why
Contract:   the shared interface (API shape, event, config key), identical text in every brief that touches it
Order:      lands before/after <repo>; what to wait for before starting
Acceptance: observable checks
Verify:     commands that prove them
Non-goals:  what stays untouched
Report:     how to reach the orchestrator (adapter command)
```

- Write the contract once and paste it verbatim. If two briefs disagree on it, the plan is wrong.
- Merge order: providers before consumers, config before the code that reads it, migrations before code that needs them.
- A brief holds only what the manager can't get from the repo. Tickets are the manager's job.
- For a large or vague story, run **big-plan** before splitting it into briefs.

## 3. Start or reuse managers

One manager per repo, one repo per manager. If the repo already has an open manager (in Orca, a kept-open session), send it the new brief instead of starting a second one. Otherwise start one with the repo's `repo_config` row for `manager` (falling back to `repo='*'`).

When a brief or follow-up creates a new Orca dispatch for a manager, the sender records that new ID in `tickets.manager_dispatch` for all unfinished tickets owned by the manager. Use the send receipt and follow the adapter's dispatch tracking rule for the update.

Start the repos that land first first. Later repos can plan in parallel when their brief says what to wait for.

## 4. Answer, relay, escalate

When a manager writes:
- Answer anything the story, contract, order or code already settles. Decide, and state your pick in one line.
- Cross-repo order lives in `tickets.depends_on`. When a provider ticket reaches `review`, send its branch and head commit (`git -C <provider> rev-parse <branch>`) to the manager of every ticket that depends on it, without waiting to be asked. Include the provider path so its reviewer can check shared fixtures.
- Escalate to the owner only: contract or merge-order changes, scope changes, anything irreversible (merging, pushing to main, deleting branches or data), spending, and genuine uncertainty. Batch them into one question with a recommended option.
- The owner can talk to a manager directly. That overrides you; update your plan.
- When the owner says “ticket X pakai <harness/model>”, relay it to the owning manager as an override for that ticket. Include the role and any effort or mode the owner specified, and have the manager record it in `tickets.roles`. Repo defaults remain in `repo_config`.
- Relay any manager proposal to the owner with the role, harness/model and reason, with keeping defaults as the default option. Wait for the owner's decision and relay it before the manager applies any override.
- Relay first-time integration branch choices as an interactive question, recommended option first. When the owner changes a repo's integration branch, have its manager update `repo_settings.base`. For a story or ticket exception, have the manager set `tickets.base` on the affected tickets.

## 5. Report

Use the story board query from the db README. Per repo: tickets done, in review or blocked, PR links, verify results. A failing verify is reported as failing.

## Rules
- Never code. Never merge. Never push.
- Don't read worker or reviewer output; managers summarise for you.
- Don't poll. Wait for messages the way your adapter describes.
- Spend the owner's attention on decisions only.
