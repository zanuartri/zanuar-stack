# Orca adapter

How the four roles map onto [Orca](https://github.com/stablyai/orca)'s `orca orchestration` commands. Run `orca orchestration <cmd> --help` for the full flags; this page covers only what the skills need.

The ticket db stays the source of truth for tickets and runs. Orca carries the sessions and the messages.

## Roles at a glance

| role | started by | how | stays open |
|---|---|---|---|
| lead | owner | an ordinary Orca agent session with the `lead` skill | yes |
| manager | lead (or owner) | `worker-start --keep-open` in the repo | yes, reused per repo |
| worker | manager | `worker-start` in a new child worktree (mode `orca`) or headless | until PASS |
| reviewer | manager | headless in the worker's worktree (default) or `worker-start` | no |

## Lead → manager

Start one manager per repo and keep it open so later briefs reuse it:

```sh
orca orchestration worker-start --keep-open \
  --repo path:<repo> --worktree current \
  --agent <harness> --model <model> --effort <effort> \
  --task-title "manager: <repo>" \
  --spec-file brief-<repo>.md
```

Before starting, check for a live one with `orca orchestration worker-list` (or `task-list`). If the repo already has a kept-open manager, send the brief to it instead:

```sh
orca orchestration send --to dispatch:<id> --subject "brief S-12" --body-file brief-<repo>.md
```

The lead waits with `orca orchestration check` (Orca wakes it on new mail) and answers with `orca orchestration reply --id <message_id> --body "…"`.

## Manager → worker (mode `orca`)

```sh
orca orchestration worker-start \
  --repo path:<repo> --worktree new-child --name t-<id> --base-branch <base> \
  --agent <worker harness> --model <model> --effort <effort> \
  --task-title "T-<id> <title>" \
  --spec "You are the worker for ticket <id> in ~/.orca/tickets/tickets.db. Load the worker skill."
```

The worker reports with `orca orchestration send --type worker_done …` and asks with `orca orchestration ask …`; the manager receives both through `check`. `worker-read` shows bounded output when a worker goes quiet. Steer with `send --to dispatch:<id>`, stop with `worker-stop`.

## Kept-open sessions

- Managers: always `--keep-open`. Idle managers cost nothing and keep repo context between stories.
- Workers: keep open (`worker-keep-open`) until the reviewer PASSes, because FIX findings go back to the same session. Release with `worker-release` after the PR is open.
- Reviewers: one-shot.

## Headless mode

For `mode = headless` (the reviewer's default), the manager makes the worktree itself and runs the harness non-interactively in it:

```sh
git -C <repo> worktree add ../wt/t-<id> -b t/<id>-<slug> <base>   # workers only; reviewers reuse the worker's tree
cd ../wt/t-<id>
```

| harness | one-shot command |
|---|---|
| claude | `claude -p "<prompt>" --model <model>` |
| codex | `codex exec "<prompt>"` (add `-m <model>`) |
| omp | `omp -p "<prompt>"` |
| commandcode | `commandcode -p "<prompt>"` |

Flags differ per harness and version; check its `--help`. Run it as a background command so the manager is woken when it exits, and read the verdict or report from its final output. Record the run in `runs` with `mode='headless'`.

Remove a headless worktree after its PR merges: `git -C <repo> worktree remove ../wt/t-<id>`.

## Watching PRs

Prefer an Orca automation over polling: `orca automations create` with a trigger on the PR's `github.ci_*` events that messages the owning session. Remove it when the PR is ready (`orca automations remove`). See `skills/watch-pr`.
