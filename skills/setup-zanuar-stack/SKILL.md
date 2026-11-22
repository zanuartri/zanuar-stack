---
name: setup-zanuar-stack
description: "Set up machine defaults even before any repos exist. Rerun for each new repo to record its roles, autonomy, landing policy and integration branch."
disable-model-invocation: true
---

# Setup zanuar-stack

Gets the shared state ready that the `orchestrator`, `manager`, `worker` and `reviewer` skills (this pack's, not look-alikes such as `rig-manager`) assume:

- the ticket db at `~/.orca/tickets/tickets.db`, built from [`schema.sql`](schema.sql)
- `repo_config` sets machine-wide (`repo='*'`) and repo defaults for each role. Managers record owner-approved ticket overrides in `tickets.roles`.

Explore, show what you found, ask, then write. Safe to re-run: the schema is idempotent and rows are replaced, not duplicated.

## Choose a mode

Ask for **full** (ticket db, default) or **lite** (briefs and status in chat). In lite, skip DB initialization and use the launch and base settings agreed in chat. Carry the explicit choice in every role's prompt, even if a DB already exists. Without an explicit choice, role sessions use full if the configured DB exists (`ZANUAR_DB` or the default path above), otherwise lite.

## Python

Use `python3` with the scripts next to this file. They use only the standard library. Re-running `init_db.py` also migrates an older db. On Windows use `python` or `py -3` if `python3` is unavailable. Use `-` for an unset model or effort. For multiline SQL or parameters, use `tq.py --file query.sql --params-file params.json`.

On Windows, set `$env:PYTHONIOENCODING = 'utf-8'`. Write files with Python and explicit UTF-8 encoding. Avoid PowerShell pipelines that add a BOM.

## 1. Explore

- Run `python3 init_db.py` from this skill's directory to initialize the db, then `python3 init_db.py show` to list the current settings.
- For machine setup, use `*` even if there are zero repos. Skip the integration branch step. When a repo is added later, rerun for its absolute git root and leave machine defaults in place. If scope is unclear inside a repo, ask which scope applies.
- Run `python3 init_db.py detect` to find harness binaries on `PATH` and list existing user skills directories, including `~/.claude/skills`, `~/.codex/skills`, `~/.omp/agent/skills`, `~/.commandcode/skills` and `~/.agents/skills`. Offer only harnesses with binaries on `PATH`. On macOS a Homebrew-installed harness is detected when its bin directory is on `PATH`.
- Check which harnesses the session adapter can launch on the execution host. Record them in the setup summary.

## 2. Ask, one role at a time

Roles in order: **manager**, **worker**, **reviewer**. For each, ask four things, leading with a recommendation the owner can accept in one word:

Recommend a stronger model for manager that can reliably follow the full dispatch, review, and PR protocol. Recommend cheaper models for worker and reviewer. S-4's Haiku/Flash-class models did well in those roles, but as managers they skipped review and pushed directly to base.

| field | ask | default |
|---|---|---|
| harness | one of the detected harnesses | the one running this setup |
| model | an id from that harness's own list (below) | the harness's current default |
| effort | what that harness accepts (e.g. `low`/`medium`/`high`) | `high` for reviewer, `medium` otherwise |
| mode | managed session or `headless` (one-shot run in a worktree) | managed session for manager and worker, `headless` for reviewer |

**Never guess a model id.** Read it from the harness, and show the owner a short list:

| harness | list models |
|---|---|
| omp | `omp models` (or `omp models find <pattern>`) |
| codex | `codex debug models` (JSON; use the `slug` values) |
| commandcode | `commandcode --list-models` |
| pi | `pi --list-models [search]` |
| opencode | `opencode models` |
| claude | no list command: offer the aliases `opus`, `sonnet`, `haiku`, or a full id the owner reads from `/model` |

If the list command fails, say so and ask the owner for the id. When Orca cannot set the requested model or effort, use headless for that configuration. Use `-` only when the owner approves leaving the setting unset.

Before saving, use the adapter to verify launch-time model and effort for managed roles. Save the effective mode in `repo_config`. Use `headless` for a worker or reviewer whose settings need it. The manager needs a launchable session.

Then ask for autonomy once for the same scope:

| field | ask | default |
|---|---|---|
| autonomy | `ask` (confirm after each ticket), `review` (agents loop alone, ask before merge), `merge` (merge when review, verify and PR checks are green) | `review` |

Set `land=pr` for machine defaults and hosted repos. For a repo the owner chose to keep local, set `land=local` for reviewed branch handoff.

Tell the owner that `merge` permits automatic merges into the repo's non-production integration branch. The GitHub default branch and `main`/`master` always require explicit approval.

### Integration branch

Use the base already agreed for a new repo, including a local-only repo. If the repo has a saved base, keep it unless the owner changes it. Otherwise detect the hosted default and look for `develop`, `staging` or `dev` among the remote branches. If there is an alternative, ask once with a recommendation first and the hosted default among the options. With no alternative, use the hosted default. For a local repo with no agreed base, check its branches and ask which to use. Save the branch name.

## 3. Write

From this skill's directory, replace the example values and run one call per role. Quote `'*'` when setting the machine default.

```sh
python3 init_db.py set '*' worker codex - - headless
```

and one for the settings:

```sh
python3 init_db.py settings '*' review pr
```

Save a repo's integration branch choice with `python3 init_db.py base <repo> <branch>`.

Run `python3 init_db.py show` (or pass the repo path after `show`) and read the rows back to the owner.

## 4. Done

Start with the `orchestrator` skill for a new project or work across repos. Use the `manager` skill for one configured repo. Managers read the saved rows.
