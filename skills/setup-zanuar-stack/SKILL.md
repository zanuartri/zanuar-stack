---
name: setup-zanuar-stack
description: "Set up zanuar-stack on this machine or repo: create the ticket db, detect installed agent harnesses, and record which harness, model, effort and mode plays manager, worker and reviewer. Run once per machine, and once per repo that needs its own roles, before the first orchestrator or manager session."
disable-model-invocation: true
---

# Setup zanuar-stack

Gets the shared state ready that the `orchestrator`, `manager`, `worker` and `reviewer` skills (this pack's, not look-alikes such as `rig-manager`) assume:

- the ticket db at `~/.orca/tickets/tickets.db`, built from [`schema.sql`](schema.sql)
- `repo_config` rows: who plays each role, machine-wide (`repo='*'`) or for one repo

Explore, show what you found, ask, then write. Safe to re-run: the schema is idempotent and rows are replaced, not duplicated.

## Python on Windows

Every step runs `init_db.py` next to this file with Python's stdlib only. On Windows run it from **PowerShell**: Git Bash `python` is often a pyenv/Store shim that mangles arguments. In PowerShell 5.1 an empty `''` argument is dropped, so the script takes `-` for "no model / no effort". Re-running `init_db.py` also migrates an older db (new tables and columns). Agents run other queries through `tq.py sql "<SQL>" [params...]` next to this file, so nobody hand-quotes SQL.

## 1. Explore

- Db: `python <this dir>/init_db.py` creates it if missing and prints its path. Then `python <this dir>/init_db.py show` lists existing `repo_config` rows. Tell the owner what is already set.
- Scope: inside a git repo (`git rev-parse --show-toplevel`), ask whether these answers are the machine default (`*`) or for this repo only (store the repo's absolute path, forward slashes, e.g. `C:/code/app`). Outside a repo, it's `*`.
- Harnesses: check which are on `PATH` (PowerShell `Get-Command claude,codex,omp,commandcode,opencode,pi -ErrorAction SilentlyContinue`, or `command -v` in a POSIX shell). Offer only the ones found.

## 2. Ask, one role at a time

Roles in order: **manager**, **worker**, **reviewer**. For each, ask four things, leading with a recommendation the owner can accept in one word:

| field | ask | default |
|---|---|---|
| harness | one of the detected harnesses | the one running this setup |
| model | an id from that harness's own list (below) | the harness's current default |
| effort | what that harness accepts (e.g. `low`/`medium`/`high`) | `high` for reviewer, `medium` otherwise |
| mode | `orca` (own Orca session) or `headless` (one-shot run in a worktree) | `orca` for manager and worker, `headless` for reviewer |

**Never guess a model id.** Read it from the harness, and show the owner a short list:

| harness | list models |
|---|---|
| omp | `omp models` (or `omp models find <pattern>`) |
| codex | `codex debug models` (JSON; use the `slug` values) |
| commandcode | `commandcode --list-models` |
| pi | `pi --list-models [search]` |
| opencode | `opencode models` |
| claude | no list command: offer the aliases `opus`, `sonnet`, `haiku`, or a full id the owner reads from `/model` |

If the list command fails, say so and ask the owner for the id instead of inventing one. A harness Orca can't configure (see the adapter: commandcode and others ignore `--model`/`--effort`) gets model `-` and effort `-`.

Then ask two things once, for the same scope:

| field | ask | default |
|---|---|---|
| autonomy | `ask` (confirm after each ticket), `review` (agents loop alone, ask before merge), `merge` (merge when review, verify and PR checks are green) | `review` |
| land | `pr` (push and open a PR) or `local` (squash into the base, no PR) | `pr` |

Tell the owner that `merge` is their standing OK for agents to merge in that scope.

## 3. Write

One call per role:

```powershell
python <this dir>/init_db.py set <repo|*> <role> <harness> <model|-> <effort|-> <orca|headless>
```

and one for the settings:

```powershell
python <this dir>/init_db.py settings <repo|*> <ask|review|merge> <pr|local>
```

Then `python <this dir>/init_db.py show <repo>` and read the rows back to the owner.

## 4. Done

Tell the owner the next step: start a session with the `orchestrator` skill (several repos) or the `manager` skill (one repo). Managers read these rows and won't ask again.
