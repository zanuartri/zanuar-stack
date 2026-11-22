# Ticket database

The shared SQLite database defaults to `~/.orca/tickets/tickets.db`. Use `ZANUAR_DB` to select a different file. Use a consistent absolute path with forward slashes for each ticket's `repo` key.

| Table | Contents |
|---|---|
| `stories` | Cross-repo goals |
| `tickets` | Scope, acceptance, verification, status, branch, PR, policy and role overrides, manager dispatch and dependencies |
| `runs` | Worker, manager and reviewer attempts and results |
| `repo_config` | Default harness, model, effort and mode per role |
| `repo_settings` | Autonomy, landing policy and integration branch |
| `decisions` | Evidence for decisions made during a ticket |
| `pr_watch` | Last seen PR state, owned by the watcher |

## Initialize and query

From the zanuar-stack checkout, run:

```sh
python3 skills/setup-zanuar-stack/init_db.py
python3 skills/setup-zanuar-stack/init_db.py set '*' worker codex - - orca
python3 skills/setup-zanuar-stack/init_db.py show
```

Pass values as parameters to `tq.py`. SELECT returns one JSON object per line. INSERT returns the row ID, and other writes return the changed row count. Positional parameters are strings, with `-` representing SQL NULL.

```sh
tq=skills/setup-zanuar-stack/tq.py
repo=$(git rev-parse --show-toplevel)

# Roles for this repo, then machine defaults
python3 "$tq" sql "SELECT * FROM repo_config WHERE repo IN (?, '*') ORDER BY repo='*', role" "$repo"

# Open tickets and one ticket in full
python3 "$tq" sql "SELECT id,story,title,status,branch,fix_rounds FROM tickets WHERE repo=? AND status NOT IN ('done','canceled')" "$repo"
python3 "$tq" sql "SELECT * FROM tickets WHERE id=?" 12

# Move to review and count a fix round
python3 "$tq" sql "UPDATE tickets SET status='review', review_at=datetime('now') WHERE id=?" 12
python3 "$tq" sql "UPDATE tickets SET status='in-progress', fix_rounds=fix_rounds+1 WHERE id=? AND status='review'" 12

# Start and end a run (replace the example run ID with the returned ID)
python3 "$tq" sql "INSERT INTO runs(ticket,role,harness,model,effort,mode) VALUES (?,?,?,?,?,?)" 12 worker codex - - orca
python3 "$tq" sql "UPDATE runs SET ended=datetime('now'), result=? WHERE id=?" done 42

# Story board
python3 "$tq" sql "SELECT repo,id,title,status,pr_url FROM tickets WHERE story=? ORDER BY repo,id" S-12
```

## Ticket transitions

```text
queued --all depends_on tickets done--> todo
todo --> in-progress --> review
review --FIX from reviewer, CI or PR comment--> in-progress --> review
review --owner decision needed--> needs-you --> in-progress or review
any --record the reason--> blocked --> in-progress
review --PR merged--> done
any --> canceled
```

The manager writes each transition. On FIX, update the status and increment `fix_rounds` together before returning the work to the same worker. On cancellation, downstream tickets still need their dependencies resolved. The PR watcher skips canceled and done tickets.

## Integration branch

`tq.py resolve-base <ticket> <github-default-branch>` uses `tickets.base`, then the repo's own `repo_settings.base`, then the default from `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`. Set the repo branch with `init_db.py base <repo> <branch>` (use `-` for the GitHub default). For a story or ticket exception, set `tickets.base` on each affected ticket.

## Per-ticket roles

`tickets.roles` is nullable text containing a JSON object keyed by `worker` or `reviewer`. The manager resolves each field in this order: `ticket.roles` (the ticket's `roles` column) > `repo_config[repo]` > `repo_config['*']`. An absent role, missing field, or JSON null inherits the next available value. Record what actually ran in `runs`.

Use per-ticket harness and model overrides only when the owner requests them for that ticket or explicitly confirms a proposal. For example, a ticket can store these overrides:

```json
{"worker":{"harness":"claude","model":"<model-id>","effort":"high"},"reviewer":{"mode":"headless"}}
```

To update ticket 12, save `["{\"worker\":{\"effort\":\"high\"}}",12]` in `update-roles.json`. The first parameter is the JSON patch as a string. `json_patch` preserves other overrides and removes keys set to JSON null.

```sh
printf '%s\n' "UPDATE tickets SET roles=json_patch(coalesce(roles, '{}'), json(?)) WHERE id=?" > update-roles.sql
python3 "$tq" --file update-roles.sql --params-file update-roles.json
python3 "$tq" resolve-role 12 worker
python3 "$tq" resolve-role 12 reviewer
```

## Multiline SQL and parameters

Save the statement as UTF-8 `new-ticket.sql`:

```sql
INSERT INTO tickets(repo, story, title, goal, acceptance, verify, scope, status, depends_on)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
```

Save the values in order as a UTF-8 JSON array in `ticket.json`. For `status` and `depends_on`, use `"todo", null` for a ready ticket or `"queued", "12,14"` for a ticket waiting on tickets 12 and 14. Use `null` for SQL NULL and `\n` for line breaks within a value. Named SQLite placeholders also accept a JSON object.

```sh
python3 "$tq" --file new-ticket.sql --params-file ticket.json
python3 "$tq" --file - --params-file ticket.json < new-ticket.sql
python3 "$tq" --file new-ticket.sql --params-file - < ticket.json
```

The last two examples show alternate input methods for the same insert. Only one input can use stdin per call. On Windows PowerShell, use the first command with both files and replace `python3` with `python` or `py -3` if needed. This avoids passing multiline content and embedded JSON quotes through native command arguments.
