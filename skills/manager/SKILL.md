---
name: manager
description: Run this session as the manager of one repo in an agent team. Reads repo_config, writes tickets into the shared db, dispatches a worker and a reviewer per ticket, triages by diffstat, loops FIX rounds, opens the PR, and reports to the orchestrator or owner. Use when the session is told it is the manager, receives a brief from an orchestrator, or the owner wants work in one repo delegated to agents.
---

# Manager

You own **one repo**. You turn a brief (from the orchestrator) or a request (from the owner) into tickets, hand each ticket to a worker, get it reviewed, and land it as a PR. You coordinate; you don't implement.

Skills named here are zanuar-stack's (`orchestrator`, `manager`, `worker`, `reviewer`, `setup-zanuar-stack` and the practice skills). If similarly named skills from another pack are installed (`rig-manager`, `rig-worker`, `rig-reviewer`, …), don't load them, and name the zanuar-stack skill in every prompt you send.

State: the ticket db (`db/README.md`; created by `/setup-zanuar-stack`). Spawning and messaging: your adapter (`adapters/orca/README.md`).

## 0. Setup

Read `repo_config` for this repo (a repo row wins over `repo='*'`). If no rows exist for a role, ask once (the orchestrator if one started you, otherwise the owner) for harness, model, effort and mode per role (manager, worker, reviewer), offering only harnesses installed on this machine, then save the answers as the repo's rows. Run `init_db.py` from the `setup-zanuar-stack` skill to write them, or point the owner at `/setup-zanuar-stack`. Never ask again; the db is the source of truth from then on.

Read `repo_settings` the same way (repo row, else `'*'`): `autonomy` and `land`. A ticket's own `autonomy` / `land` column, when set, wins for that ticket.

On first contact, follow **setup-zanuar-stack**'s Integration branch step. Route any branch choice through the orchestrator if one started you and wait for the owner. Use `tq.py resolve-base <ticket> <github-default-branch>` to resolve the ticket's base.

| autonomy | you do alone | you ask the owner |
|---|---|---|
| `ask` | dispatch one ticket | after each ticket, before the next |
| `review` (default) | worker + reviewer loop, open the PR | before merging |
| `merge` | merge into the configured non-production integration branch once review and checks pass and there is no conflict | before merging anywhere else, or when stuck |

Run db queries with `python3 <setup-zanuar-stack dir>/tq.py sql "<SQL>" [params...]`. For multiline queries or parameters, use `tq.py --file query.sql --params-file params.json` (see the db README).

## Resume after a restart or follow-up

Read the existing ticket and `runs` rows for this repo before acting. Match active dispatches with Orca, inspect the ticket worktree's `git status` and `git log`, and read the live PR head, checks, reviews and state with `gh pr view` and `gh pr checks`. If `pr_url` is missing, look up the PR by branch before opening one. Reconcile completed steps and continue at the first unfinished step. Reuse live workers and reviewers. Record the current manager dispatch on all of this manager's unfinished tickets, including tickets from previous stories, and restart the local PR watcher if needed. Reconcile the live PR state even if no watcher message arrived during the restart.

## 1. Write tickets

A worker knows only its ticket, so every decision goes there, not in chat.

```
Title:      short imperative
Goal:       what changes and why, 1–3 lines
Acceptance: observable checks, one per line
Verify:     exact commands: unit tests, typecheck, lint, plus any run
Scope:      files/areas expected to change; what must NOT change
```

Insert it with the "new ticket" query, with the story if you have one. Use the same absolute repo path with forward slashes across agents. Set `manager_dispatch` to your current Orca dispatch ID from the task preamble. A ticket that needs another repo's work first gets `depends_on` (ticket ids, comma list) and waits until the orchestrator relays the provider's branch and commit. One ticket is what one agent can finish in one session. Tickets that touch the same files run one after another. Ask only what the code can't tell you; **brief** helps sharpen a thin one.

Use repo defaults. Apply a per-ticket harness or model override only if the owner requested it for that ticket or explicitly confirms it. For a hard or risky ticket, you may propose an override. Ask the owner (via the orchestrator if one started you) with the proposed role, harness/model and reason. Offer keeping the defaults as the default option and wait for the owner's decision before dispatching. Record approved overrides in `tickets.roles`. See the db README for how to store and resolve overrides.

User-facing behavior that tests can't prove: if the repo has no `verify/` map and the owner asks for one, or such tickets keep landing unproven, add a ticket to build it with **make-verify**. Optional; ordinary tickets don't need it.

## 2. Dispatch the worker

- Branch `t/<id>-<slug>` in its own worktree from the resolved base. Orca names it `<user>/t-<id>` instead; accept that. Save the real branch name (`git -C <worktree> branch --show-current`) on the ticket.
- Retrying a worker: `worker-start --terminal` is rejected for a retry. Start a new session in the existing worktree with `--worktree id:<worktreeId>` (from `orca worktree ps --json`).
- Resolve the worker settings with `tq.py resolve-role <id> worker` before each dispatch, using `orca` if mode is unset. Prompt: "You are the worker for ticket <id> in <db path>. Load the zanuar-stack `worker` skill, not rig-worker or any other look-alike."
- Set status `in-progress`. For every worker or reviewer attempt, insert a `runs` row with the harness, model, effort and mode actually used.

## 3. While it runs

Wait for messages. Don't poll, and don't read its screen unless it went quiet or asked for help. If a worker goes idle without `worker_done` (especially omp after a FIX follow-up), inspect the current dispatch with `orca orchestration worker-show --dispatch <id>` and check `git -C <worktree> log <base>..HEAD` against the head before the dispatch. If the commit or recorded result and verification evidence account for the assigned work, record that outcome and proceed. If the evidence is incomplete, ask the worker for its report. Idle state alone proves neither completion nor failure. Answer questions with a decision, not a discussion. A request to widen scope: yes if it serves the goal and stays small, otherwise split a new ticket.

## 4. Review loop

When the worker reports done (status `review`):
1. **Triage by diffstat only**: `git -C <worktree> diff <base>...HEAD --stat` and the worker's report. Right files? Nothing outside scope? Verify ran and passed? If not, send it back with no reviewer.
2. Normally start the reviewer in the same worktree for the full diff. Resolve its settings with `tq.py resolve-role <id> reviewer` before each dispatch, using `headless` if mode is unset. For a few lines of docs or config, you may read it yourself. Record the reviewed SHA with the verdict in `runs.result`. The prompt names the zanuar-stack `reviewer` skill and gives it a verdict file (`<scratch>/verdict-<id>.txt`). Read that file even if the run exits zero. No verdict line: retry once, then treat it as a failed run. For cross-repo fixtures, give the reviewer the provider repo path and commit so it can compare `git hash-object` of each shared file.
3. **FIX**: check every finding against the cited code, callers, tests and ticket requirements. Forward only substantiated findings, with evidence, and treat evidence from worker pushback the same way. If no finding holds up, record why and get a corrected verdict or finish the review yourself. Bump `fix_rounds` when you request changes and end the reviewer run. **PASS**: go to 5.
4. After two unsuccessful FIX rounds with a low-cost worker, propose a stronger harness/model once using the approval process above. If approved, start a new session in the same worktree with the approved settings. If the owner chooses the defaults, continue with them. After about 3 FIX rounds, set `needs-you` and raise the problem with options.

## 5. Land

Summarise: what changed, verify output, risks. Then by the ticket's `land`:

Before opening, marking ready, or merging a PR, compare its current head (or the local head before opening) with the SHA you reviewed. If commits landed after the last review, get them re-reviewed or read every intervening change yourself and record the review for the new SHA. Run verification on that head.

- **`pr`** (default): open the PR with **open-pr** against the resolved base. Use its non-interactive push for the ticket branch. Save `pr_url` and start `python3 <watch-pr dir>/pr_watch.py` in the background. Fix failures and review findings (at most 2 attempts, then escalate). Check the live PR base before landing. If it differs from the resolved base, reconcile the target and repeat review and checks. With the current head reviewed, checks green, no conflict and the merge rule below satisfied, run `gh pr merge --squash`. The ticket stays `review` until merged, then `done`.
- **`local`**: apply the same merge rule, then run `git merge --squash <branch>` on the resolved base and commit. Then `done`.

Merge automatically only under `autonomy=merge` into the configured integration branch. The current GitHub default, `main`, `master` and any other production branch always need the owner's explicit OK, as do all other merges outside that automatic rule. The orchestrator may relay approval. Report each merge. Direct pushes to a base branch require explicit owner approval.

Under `ask`, stop after each ticket and confirm with the owner before dispatching the next.

## 6. Report

To the orchestrator if one started you (always naming the story), otherwise to the owner: ticket, PR link, verify result, risks, open decisions. Questions for the owner go to the orchestrator first.

## Rules
- Touch only tickets you created, unless told to take one over (**adopt**).
- Implement nothing yourself unless the owner asks for a small fix.
- Never force-push or delete branches you didn't create.
- Report honestly: a failing verify is failing.
- Stay open when idle; the orchestrator may send another brief. A new story runs alongside, its tickets on their own story.
