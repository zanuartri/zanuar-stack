# Ticket database

The shared SQLite database defaults to `~/.orca/tickets/tickets.db`. Use `ZANUAR_DB` to select a different file. Use a consistent absolute path with forward slashes for each ticket's `repo` key.

| Table | Contents |
|---|---|
| `stories` | Cross-repo goals |
| `tickets` | Scope, acceptance, verification, status, branch, PR, policy overrides, manager dispatch and dependencies |
| `runs` | Worker, manager and reviewer attempts and results |
| `repo_config` | Harness, model, effort and mode per role |
| `repo_settings` | Autonomy and landing policy |
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
python3 "$tq" sql "SELECT id,story,title,status,branch,fix_rounds FROM tickets WHERE repo=? AND status<>'done'" "$repo"
python3 "$tq" sql "SELECT * FROM tickets WHERE id=?" 12

# Move to review and count a fix round
python3 "$tq" sql "UPDATE tickets SET status='review', review_at=datetime('now') WHERE id=?" 12
python3 "$tq" sql "UPDATE tickets SET fix_rounds=fix_rounds+1 WHERE id=?" 12

# Start and end a run (replace the example run ID with the returned ID)
python3 "$tq" sql "INSERT INTO runs(ticket,role,harness,model,effort,mode) VALUES (?,?,?,?,?,?)" 12 worker codex - - orca
python3 "$tq" sql "UPDATE runs SET ended=datetime('now'), result=? WHERE id=?" done 42

# Story board
python3 "$tq" sql "SELECT repo,id,title,status,pr_url FROM tickets WHERE story=? ORDER BY repo,id" S-12
```

## Multiline SQL and parameters

Save the statement as UTF-8 `new-ticket.sql`:

```sql
INSERT INTO tickets(repo, story, title, goal, acceptance, verify, scope)
VALUES (?, ?, ?, ?, ?, ?, ?)
```

Save the values in order as a UTF-8 JSON array in `ticket.json`. Use `null` for SQL NULL and `\n` for line breaks within a value. Named SQLite placeholders also accept a JSON object.

```sh
python3 "$tq" --file new-ticket.sql --params-file ticket.json
python3 "$tq" --file - --params-file ticket.json < new-ticket.sql
python3 "$tq" --file new-ticket.sql --params-file - < ticket.json
```

The last two examples show alternate input methods for the same insert. Only one input can use stdin per call. On Windows PowerShell, use the first command with both files and replace `python3` with `python` or `py -3` if needed. This avoids passing multiline content and embedded JSON quotes through native command arguments.
