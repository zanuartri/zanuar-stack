# zanuar-stack

![zanuar-stack: run your coding agents like a team](docs/hero.png)

[![Portability](https://github.com/zanuartri/zanuar-stack/actions/workflows/portability.yml/badge.svg)](https://github.com/zanuartri/zanuar-stack/actions/workflows/portability.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Why

Running many coding agents at once is easy. Keeping track of them is not: who owns which task, what got reviewed, which PR is waiting on you.

zanuar-stack is a skill pack that gives agents a small team structure. One **orchestrator** plans across repos, one **manager** per repo turns briefs into tickets, and a **worker** and **reviewer** handle each ticket in its own worktree. You make the decisions; they keep the books. Built for [Orca](https://github.com/stablyai/orca) first, but the skills only assume a harness that can start another agent and pass messages.

## Quick start

1. **Install** for your harness (see [Install](#install)).
2. Run **`/setup-zanuar-stack`** once. It creates the ticket database and asks who plays manager, worker and reviewer.
3. Start a session and give it a role:

```text
act as orchestrator: add rate limiting to the API and show the limit in the dashboard
act as manager for this repo: fix the flaky login test and open a PR
```

The orchestrator interviews you, writes one brief per repo and starts a manager for each. The manager splits the work into tickets, dispatches workers, has each reviewed, and opens PRs. You hear back when a decision is yours.

## How it works

```
                 owner
                   │  decisions only
                   ▼
             orchestrator ── interview → story + one brief per repo
        ┌──────────┼──────────┐
        ▼          ▼          ▼
     manager    manager    manager      one per repo, kept open
      │    │
      ▼    ▼
   worker reviewer                      one ticket, own worktree/branch
      │    ▲
      └────┘  FIX rounds (max ~3) → PASS → PR
```

Shared state is one SQLite file, `~/.orca/tickets/tickets.db` (see [`db/`](db/README.md)): stories, tickets, runs, per-repo role config.

- **Ticket statuses:** `queued` (waiting on dependencies) → `todo` → `in-progress` → `review` → `done`. Also `needs-you` (owner decision), `blocked` and `canceled`.
- **FIX loop:** a reviewer, CI failure or PR comment that needs a change sends the ticket back to the same worker and worktree (`review` → `in-progress` → `review`). After a few rounds it escalates instead of looping.
- **Autonomy** (per repo, per-ticket override): `ask` stops after each ticket, `review` (default) opens the PR and asks before merging, `merge` merges into a non-production integration branch once review and checks pass.
- **Land:** `pr` opens a pull request; `local` hands over the reviewed branch for repos with no remote.
- **Integration/base branch:** each repo has a saved base. Nothing is pushed to it directly; every change goes through a PR. Production branches always need your explicit OK.
- **Overrides:** repo defaults pick each role's harness and model. A per-ticket override applies only with the owner's approval.
- **PR watcher:** a local script (`pr_watch.py`) tracks CI, reviews and comments on open PRs and reports to the manager. No hosted service.
- **One voice:** with an orchestrator running, it is the only agent that talks to you. A manager talks to you directly only when you started it.

For a [new project or repo](skills/orchestrator/SKILL.md#new-project-or-repo), initialize and register it before briefing its manager on the first skeleton ticket. Harness wiring: [`adapters/orca`](adapters/orca/README.md).

## Skills

| role skills | |
|---|---|
| [`orchestrator`](skills/orchestrator/SKILL.md) | cross-repo planning, briefs, escalation; never codes |
| [`manager`](skills/manager/SKILL.md) | tickets, dispatch, triage, review loop, PR |
| [`worker`](skills/worker/SKILL.md) | one ticket, verify, report |
| [`reviewer`](skills/reviewer/SKILL.md) | full-diff review, PASS or FIX |

| practice skills | |
|---|---|
| [`interview`](skills/interview/SKILL.md) | one-question-at-a-time requirements interview |
| [`big-plan`](skills/big-plan/SKILL.md) | design the workflow for large or unattended work |
| [`brief`](skills/brief/SKILL.md) | make a task deeper, then rewrite it |
| [`shape-first`](skills/shape-first/SKILL.md) | sketch types and boundaries before code |
| [`cut-first`](skills/cut-first/SKILL.md) | subtract before you add |
| [`root-cause`](skills/root-cause/SKILL.md) | fix where it first went wrong |
| [`test-first`](skills/test-first/SKILL.md) | failing regression test, then fix |
| [`ripple-check`](skills/ripple-check/SKILL.md) | what breaks outside the diff, proven |
| [`comment-sweep`](skills/comment-sweep/SKILL.md) | delete comments that don't earn their place, encode real constraints |
| [`make-verify`](skills/make-verify/SKILL.md) | repo-local recipe to launch the app and prove a feature (optional) |
| [`design-handoff`](skills/design-handoff/SKILL.md) | shared format for design requests and implementation briefs |
| [`decision-log`](skills/decision-log/SKILL.md) | auditable trail in the db or a TSV |
| [`setup-zanuar-stack`](skills/setup-zanuar-stack/SKILL.md) | run once: ticket db + who plays each role |
| [`adopt`](skills/adopt/SKILL.md) | take over a PR or branch, keep credit |
| [`open-pr`](skills/open-pr/SKILL.md) | short, readable PRs |
| [`watch-pr`](skills/watch-pr/SKILL.md) | own a PR through CI and review |
| [`pr-comments`](skills/pr-comments/SKILL.md) | attributed, direct PR comments |

Harness wiring: [`adapters/orca`](adapters/orca/README.md).

## Install

Pick **one** route per agent. A plugin updates itself; skills.sh and manual copies are files you own and update by hand. Installing both gives you every skill twice.

### Claude Code (plugin, updates itself)

```sh
claude plugin marketplace add zanuartri/zanuar-stack
claude plugin install zanuar-stack@zanuar-stack
```

### Codex (plugin, updates at startup)

```sh
codex plugin marketplace add zanuartri/zanuar-stack
codex plugin add zanuar-stack@zanuar-stack
```

Codex also reads `~/.agents/skills`, where skills.sh installs for Pi and others. On one machine use **either** the Codex plugin **or** skills.sh for Codex, never both (every skill appears twice). If other harnesses already use skills.sh, prefer skills.sh for Codex too. Same for Claude Code: the plugin **or** a skills.sh link, not both.

Both plugins read the same `.claude-plugin/` manifests, which point at `skills/`. A new release reaches users when `version` in `.claude-plugin/plugin.json` changes.

### Everything else (skills.sh, manual updates)

```sh
npx skills@latest add zanuartri/zanuar-stack -g -a pi
```

Replace `pi` with the agent ID from the table.

| agent | `-a` id | lands in |
|---|---|---|
| OpenCode | `opencode` | `~/.config/opencode/skills` |
| Pi | `pi` | `~/.agents/skills` |
| Command Code | `command-code` | `~/.commandcode/skills` |

Take every skill, including `setup-zanuar-stack`. Update with `npx skills@latest update -g`, and re-run `add` to pick up new skills. `-a '*'` or omitting `-a` covers any other agent skills.sh knows.

### oh-my-pi (omp): manual copy

skills.sh has no omp target. Copy the folders into omp's skills dir, `~/.omp/agent/skills`:

```sh
git clone https://github.com/zanuartri/zanuar-stack "${TMPDIR:-/tmp}/zanuar-stack"
mkdir -p "$HOME/.omp/agent/skills"
cp -R "${TMPDIR:-/tmp}/zanuar-stack/skills/." "$HOME/.omp/agent/skills/"
```

On Windows PowerShell:

```powershell
git clone https://github.com/zanuartri/zanuar-stack $env:TEMP\zanuar-stack
New-Item -ItemType Directory -Force $HOME\.omp\agent\skills
Copy-Item -Recurse -Force $env:TEMP\zanuar-stack\skills\* $HOME\.omp\agent\skills\
```

Pull and copy again to update.

### Then, once per machine

Run **`/setup-zanuar-stack`**. It creates `~/.orca/tickets/tickets.db`, finds the harnesses you have, and asks who plays manager, worker and reviewer (harness, model, effort, mode). Then start a session with the `orchestrator` skill (several repos) or the `manager` skill (one repo).

## Requirements

- Git, and the GitHub CLI (`gh`) logged in
- Python 3 (standard library only)
- Optionally [Orca](https://github.com/stablyai/orca), for managed worktrees and agent messaging
- Linux, macOS or Windows

## Lite mode

Choose lite at setup to run without a ticket database. The roles use text briefs in prompts and PRs, retain worker and reviewer handoffs, and report status in chat. Lite has no persisted ticket history, story board, KPIs, DB-backed watcher or per-ticket role overrides. Use `gh pr checks <n> --watch` for CI and TSV for the decision log. Each practice skill can also be used on its own without a ticket database.

## Credits

Adapted, in our own words, from:

| our skill | adapted from | source |
|---|---|---|
| orchestrator, manager, worker, reviewer | the role split | [herdr-rig](https://github.com/zanuartri/herdr-rig) |
| `interview` | "grill me" | Matt Pocock |
| `big-plan` | `figure-it-out` | Poteto's pstack |
| `brief` | `sharpen` | Poteto's pstack |
| `shape-first` | `architect` | Poteto's pstack |
| `decision-log` | `show-me-your-work` | Poteto's pstack |
| `test-first` | `tdd` | Poteto's pstack |
| `root-cause` | `principle-fix-root-causes` | Poteto's pstack |
| `cut-first` | `principle-subtract-before-you-add` | Poteto's pstack |
| `ripple-check` | `blast-radius` | Poteto's pstack |
| `comment-sweep` | `no-comments` | Poteto's pstack |
| `make-verify` | `create-verification-skill`, `maintain-verification-skill` | Poteto's pstack |
| `adopt` | `takeover` | [t3dotgg/tstack](https://github.com/t3dotgg/tstack) |
| `open-pr` | `file-pr` | t3dotgg/tstack |
| `watch-pr` | `babysit-pr` | t3dotgg/tstack |
| `pr-comments` | `leaving-pr-comments` | t3dotgg/tstack |

Poteto's pstack: [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack), mirror [backnotprop/pstack](https://github.com/backnotprop/pstack).

## License

MIT, see [LICENSE](LICENSE).
