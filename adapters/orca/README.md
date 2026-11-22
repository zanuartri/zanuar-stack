# Orca adapter

How the four roles map onto [Orca](https://github.com/stablyai/orca)'s `orca orchestration` commands. Run `orca orchestration <cmd> --help` for the full flags; this page covers only what the skills need.

The ticket db stays the source of truth for tickets and runs. Orca carries the sessions and the messages.

Skill names below are this pack's: `orchestrator`, `manager`, `worker`, `reviewer`, `setup-zanuar-stack`. If the harness also has look-alikes from another pack (`rig-manager`, `rig-worker`, `rig-reviewer`, …), spawn prompts must name the zanuar-stack skill and agents must not load the others.

## Roles at a glance

| role | started by | how | stays open |
|---|---|---|---|
| orchestrator | owner | an ordinary Orca agent session with the `orchestrator` skill | yes |
| manager | orchestrator (or owner) | `worker-start --keep-open` in the repo | yes, reused per repo |
| worker | manager | `worker-start` in a new child worktree (mode `orca`) or headless | until PASS |
| reviewer | manager | headless in the worker's worktree (default) or `worker-start` | no |

## Orchestrator → manager

Start one manager per repo and keep it open so later briefs reuse it:

```sh
orca worktree ps --json      # find the repo's row; copy its worktreeId
orca orchestration worker-start --keep-open \
  --worktree id:<repoId>::<abs path> \
  --agent <harness> --model <model> --effort <effort> \
  --task-title "manager: <repo>" \
  --spec-file brief-<repo>.md
```

Pass the row's `worktreeId` as `id:<worktreeId>` (it already has the form `<repoId>::<abs path>`). `path:<abs>` can fail to match even for a correct path, so don't rely on it. Don't combine `--worktree` with `--repo`, `--name` or `--base-branch`: those only apply when creating a worktree (`new-child`, `new-top-level`), and `current` means the caller's own worktree, not the repo's.

On Windows give paths in native form, `C:/code/app` or `C:\code\app`, never Git Bash's `/c/code/app`: Orca resolves them itself and the POSIX form doesn't exist for it. This applies to `--spec-file`, `--repo path:` and anything else passed to `worker-start`.

`--model` / `--effort` work only for agents Orca can configure: Claude, Codex, Cursor, Antigravity, Grok, Muse, OMP (model selector; effort = thinking level) and Pi. Other agents (e.g. commandcode) ignore them and use the model from their own config, so drop both flags for those.

Before starting, check for a live one with `orca orchestration worker-list` (or `task-list`). If the repo already has a kept-open manager, send the brief to it instead:

```sh
orca orchestration send --to dispatch:<id> --subject "brief S-12" --body-file brief-<repo>.md
```

The orchestrator waits with `orca orchestration check` (Orca wakes it on new mail). `check` takes no `--from`: it reads the calling session's own mailbox (`--terminal <handle>` only to read another). It answers with `orca orchestration reply --id <message_id> --body "…"`.

## Manager → worker (mode `orca`)

```sh
orca orchestration worker-start \
  --repo path:<repo> --worktree new-child --name t-<id> --base-branch <base> \
  --agent <worker harness> --model <model> --effort <effort> \
  --task-title "T-<id> <title>" \
  --spec "You are the worker for ticket <id> in ~/.orca/tickets/tickets.db. Load the zanuar-stack `worker` skill, not rig-worker or any other look-alike."
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
| commandcode | `commandcode -p "<prompt>" --yolo --max-turns 24` |

Flags differ per harness and version; check its `--help`. Run it as a background command so the manager is woken when it exits, and read the verdict or report from its final output. Record the run in `runs` with `mode='headless'`.

Remove a headless worktree after its PR merges: `git -C <repo> worktree remove ../wt/t-<id>`.

## Retries and quiet workers

- `worker-start --terminal <handle>` is rejected for a retry. Start a fresh session in the same worktree with `--worktree id:<worktreeId>`.
- Orca names child branches `<user>/t-<id>`. Record that real name on the ticket.
- A worker (omp in particular) can go idle without `worker_done`. Check `orca orchestration worker-show --dispatch <id>` and the worktree's `git log` before deciding.
- `orca orchestration check --wait` prints heartbeat JSON on stderr, which PowerShell reports as errors. Redirect it (`2>$null`) or run it from bash.

## commandcode as headless reviewer

`commandcode -p "<prompt>" --yolo --max-turns 24` (12 turns ran out on real tickets). Tell it to write its verdict line to a file and read that file: a run can exit 0 without a verdict. No `PASS`/`FIX` line in it: retry once.

## Watching PRs

Default: the local watcher in `skills/watch-pr/pr_watch.py`. It needs only `gh` and Python, polls GitHub with one GraphQL call per tick for every open ticket PR, and wakes the owning manager with `orca orchestration send --to dispatch:<tickets.manager_dispatch>` only when something changed. See `skills/watch-pr`.

Optional, with Orca Cloud: `orca automations create` with a trigger on the PR's `github.*` events that messages the owning session. Remove it when the PR is ready (`orca automations remove`).
