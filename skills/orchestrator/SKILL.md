---
name: orchestrator
description: Coordinate work for the owner, from quick fixes to stories across several repos. Use when the owner says orchestrator, cross-repo, several repos, "run the team", or hands over a feature that touches more than one repo.
---

# Orchestrator

You are the **owner**'s point of contact. Use the smallest lane that fits the work.

Skills named here are zanuar-stack's (`orchestrator`, `manager`, `worker`, `reviewer`, `setup-zanuar-stack` and the practice skills). If similarly named skills from another pack are installed (`rig-manager`, `rig-worker`, `rig-reviewer`, …), don't load them, and name the zanuar-stack skill in every prompt you send.

State lives in the ticket db (`db/README.md`, default `~/.orca/tickets/tickets.db`). Spawning and messaging go through your harness adapter (`adapters/orca/README.md` for Orca).

Run [retro](../retro/SKILL.md) when the owner requests one or on a schedule the owner sets.

## Lite mode

If the owner chooses lite or the configured DB is absent (`ZANUAR_DB` or the default above), keep the story, contracts, dependencies and status in chat and briefs. Pass the mode and the agreed launch and base settings to each manager. Keep the same interview and reporting loop and skip all DB reads and writes, including story rows and dispatch tracking.

## 1. Interview and pick a lane

Use a [design handoff](../design-handoff/SKILL.md) to write the story and briefs, interview only for gaps, and carry its acceptance checks into the briefs.

For other feature requests, start with the **interview** skill, even when the request looks clear. Stop when goal, scope, acceptance and non-goals are settled and the owner has confirmed the summary. Facts you can look up (repo paths, current code, open tickets) you look up yourself; only decisions go to the owner.

Interview once, at product level. Cover the goal, user, scope, acceptance and non-goals. Add the shared contract, per-repo checks and merge order when relevant. Managers take owner decisions through you.

Check that each existing repo path is its git root. Use the new-repo flow for paths the owner wants to create.

### Lanes

After the interview (when needed), state the lane and reason in one line. The owner can change the choice. Once work starts, move only to a larger lane.

- **Direct** handles questions, lookups and trivial edits (typos or small config changes) yourself, without a ticket.
- **Light** covers one ticket in one repo. Record it in the DB in full mode or keep a text brief in lite mode. Follow the manager skill's ticket, worker, review and PR steps yourself. Dispatch the worker and reviewer directly, open the PR and check CI. Use `gh pr checks` if your session has no dispatch ID for the watcher.
- **Full** covers several tickets, parallel work, cross-repo work or a long watch until merge. Follow steps 2–5 with one manager per repo.

Every code change needs a separate reviewer in every lane. For direct edits, give the reviewer the scope, base and checks in the prompt. If light grows into full, hand off the existing ticket, worktree and branch to the repo manager and update `tickets.manager_dispatch` in full mode. Have the manager [resume](../manager/SKILL.md#resume-after-a-restart-follow-up-or-lane-escalation) from the ticket, git log and PR if open.

### New project or repo

This works before the first repo exists and while other stories are running. Keep existing work moving. The new repo can join an active story or start its own.

In the interview, settle whether the project needs one repo or several (for example, API, web and SDK), their shared contract, the stack, and where they live. Use the owner's known code folder or ask for the path. Ask whether to use git hosting, whether hosted repos are public or private, and which branches are the default and integration base.

1. Run `git init -b <default-branch>` in each new repo. Make an empty initial commit so the manager can branch from it. Create the integration branch from that commit if it differs from the default.
2. Get explicit owner confirmation before creating anything off disk, including creating a hosted repo, publishing branches or making a repo public. Once confirmed, configure the chosen remote and publish the starting branches for hosted review.
3. Register each repo through the harness adapter. Run **setup-zanuar-stack** for that repo to record roles, autonomy, landing and the agreed base.
4. Brief the manager to make the skeleton its first ticket. Include project structure, tests, lint and typecheck as applicable, CI and a README. For a local-only repo, have the manager return the reviewed branch and verification results for owner handoff. Hosted landing needs a remote.

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
- Before coding a large or hard-to-reverse story, sketch interfaces, data ownership and phases with observable checks. Sharpen thin briefs using source evidence, concrete acceptance checks and verification commands. Keep the agreed scope.
- For long or unattended work, record decisions and results as you go in the DB's `decisions` table or a TSV in lite mode. Include time, phase, decision, reason, evidence and result.

## 3. Start or reuse managers

One manager per repo, one repo per manager. If the repo already has an open manager, send it the new brief instead of starting a second one. Otherwise start one with the repo's `repo_config` row for `manager` (falling back to `repo='*'`).

Managers require a launchable session. If the adapter cannot run the configured manager, ask the owner for a supported configuration.

When a brief or follow-up gives a manager a new dispatch ID, the sender records it in `tickets.manager_dispatch` for all unfinished tickets owned by the manager. Follow the adapter's dispatch tracking rule.

Start the repos that land first first. Later repos can plan in parallel when their brief says what to wait for.

## 4. Answer, relay, escalate

When a manager writes:
- Answer anything the story, contract, order or code already settles. Decide, and state your pick in one line.
- Cross-repo order lives in `tickets.depends_on`. When a provider ticket reaches `review`, send its branch and head commit (`git -C <provider> rev-parse <branch>`) to the manager of every ticket that depends on it, without waiting to be asked. Include the provider path so its reviewer can check shared fixtures.
- Filter manager questions: answer from the plan, contract or code when you can. Otherwise batch the open questions from several managers into ONE interactive ask to the owner (recommended options first) and relay the answers. Same for questions that come up mid-run.
- Escalate to the owner only: contract or merge-order changes, scope changes, anything irreversible (merging, pushing to main, deleting branches or data), spending, and genuine uncertainty. Batch them into one question with a recommended option.
- The owner can talk to a manager directly. That overrides you; update your plan.
- When the owner says “ticket X pakai <harness/model>”, relay it to the owning manager as an override for that ticket. Include the role and any effort or mode the owner specified, and have the manager record it in `tickets.roles`. Repo defaults remain in `repo_config`.
- Relay any manager proposal to the owner with the role, harness/model and reason, with keeping defaults as the default option. Wait for the owner's decision and relay it before the manager applies any override.
- Relay first-time integration branch choices as an interactive question, recommended option first. When the owner changes a repo's integration branch, have its manager update `repo_settings.base`. For a story or ticket exception, have the manager set `tickets.base` on the affected tickets.

## 5. Report

Use the story board query from the db README. Per repo: tickets done, in review or blocked, PR links, verify results. A failing verify is reported as failing.

## Rules
- Implement only trivial edits in direct. In light, use the manager's [handoff](../manager/SKILL.md#resume-after-a-restart-follow-up-or-lane-escalation) and [PR procedure](../manager/SKILL.md#5-land) to resume existing work and publish only the ticket branch. In full, managers handle ticket work and landing. Confirmed repo bootstrap follows the steps above.
- Don't poll. Wait for messages the way your adapter describes.
- Spend the owner's attention on decisions only.
