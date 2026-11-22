---
name: setup-zanuar-stack
description: "Set up zanuar-stack on this machine or repo: create the ticket db, detect installed agent harnesses, and record which harness, model, effort and mode plays manager, worker and reviewer. Run once per machine, and once per repo that needs its own roles, before the first orchestrator or manager session."
disable-model-invocation: true
---

# Setup zanuar-stack

Gets the shared state ready that the `orchestrator`, `manager`, `worker` and `reviewer` skills (this pack's, not look-alikes such as `rig-manager`) assume:

- the ticket db at `~/.orca/tickets/tickets.db`, built from [`schema.sql`](schema.sql)
- `repo_config` sets machine-wide (`repo='*'`) and repo defaults for each role. Managers record owner-approved ticket overrides in `tickets.roles`.

Explore, show what you found, ask, then write. Safe to re-run: the schema is idempotent and rows are replaced, not duplicated.

## Python

Use `python3` with the scripts next to this file. They use only the standard library. Re-running `init_db.py` also migrates an older db. On Windows use `python` or `py -3` if `python3` is unavailable. Use `-` for an unset model or effort. For multiline SQL or parameters, use `tq.py --file query.sql --params-file params.json`.

On Windows, set `$env:PYTHONIOENCODING = 'utf-8'`. Write files with Python and explicit UTF-8 encoding. Avoid PowerShell pipelines that add a BOM.

## 1. Explore

- Run `python3 init_db.py` from this skill's directory to initialize the db, then `python3 init_db.py show` to list the current settings.
- Inside a git repo, use `git rev-parse --show-toplevel` to obtain its absolute path. Ask if the settings are for that repo or for the machine default (`*`). Outside a repo, use `*`.
- Run `python3 init_db.py detect` to find harness binaries on `PATH` and list existing user skills directories, including `~/.claude/skills`, `~/.codex/skills`, `~/.omp/agent/skills`, `~/.commandcode/skills` and `~/.agents/skills`. Offer only harnesses with binaries on `PATH`. On macOS a Homebrew-installed harness is detected when its bin directory is on `PATH`.
- Compare installed harnesses with `orca agent installed --json` on the execution host. Record which harnesses Orca can launch in the setup summary.

## 2. Ask, one role at a time

Roles in order: **manager**, **worker**, **reviewer**. For each, ask four things, leading with a recommendation the owner can accept in one word:

Recommend a stronger model for manager that can reliably follow the full dispatch, review, and PR protocol. Recommend cheaper models for worker and reviewer. S-4's Haiku/Flash-class models did well in those roles, but as managers they skipped review and pushed directly to base.

| field | ask | default |
|---|---|---|
| harness | one of the detected harnesses | the one running this setup |
| model | an id from that harness's own list (below) | the harness's current default |
| effort | what that harness accepts (e.g. `low`/`medium`/`high`) | `high` for reviewer, `medium` otherwise |
| mode | `orca` (own Orca session) or `headless` (one-shot run in a worktree) | `orca` required for manager and preferred for worker, `headless` for reviewer |

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

Before saving, verify that Orca accepts the chosen launch-time model and effort for each Orca role. Record the result and save the effective mode in `repo_config`. A setup Orca cannot launch uses `headless` for worker or reviewer and is ineligible for manager.

Then ask for autonomy once for the same scope:

| field | ask | default |
|---|---|---|
| autonomy | `ask` (confirm after each ticket), `review` (agents loop alone, ask before merge), `merge` (merge when review, verify and PR checks are green) | `review` |

Set `land=pr`. All changes to base go through a PR.

Tell the owner that `merge` permits automatic merges into the repo's non-production integration branch. The GitHub default branch and `main`/`master` always require explicit approval.

### Integration branch

For a specific repo, detect its GitHub default from the repo directory with `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`. If no branch is configured, fetch origin and check its remote branches for `develop`, `staging` or `dev` distinct from the default. If any exists, ask once using an interactive question with a recommendation first and the GitHub default among the options. Save the chosen branch name, including when the owner chooses the default. If there is no alternative among those branches, use the GitHub default without asking.

## 3. Write

From this skill's directory, replace the example values and run one call per role. Quote `'*'` when setting the machine default.

```sh
python3 init_db.py set '*' worker codex - - orca
```

and one for the settings:

```sh
python3 init_db.py settings '*' review pr
```

Save a repo's integration branch choice with `python3 init_db.py base <repo> <branch>`.

Run `python3 init_db.py show` (or pass the repo path after `show`) and read the rows back to the owner.

## 4. Done

Tell the owner the next step: start a session with the `orchestrator` skill (several repos) or the `manager` skill (one repo). Managers read these rows and won't ask again.
