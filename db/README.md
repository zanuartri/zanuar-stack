# Ticket database

All shared state lives in one SQLite file: `~/.orca/tickets/tickets.db`.
Agents read and write it with Python's stdlib `sqlite3`, because the `sqlite3` CLI is often missing.
The schema is in [`schema.sql`](schema.sql).

| table | holds |
|---|---|
| `stories` | cross-repo features (`S-12 Link expiry`) |
| `tickets` | one unit of work in one repo: goal, acceptance, verify, scope, status, branch, PR, timestamps, `fix_rounds` |
| `runs` | every agent run on a ticket: role, harness, model, effort, mode, result |
| `repo_config` | who plays which role in a repo (`repo='*'` is the machine default) |
| `decisions` | optional decision trail (see `skills/decision-log`) |

Statuses: `todo → in-progress → review → done`, with `needs-you` (waiting on the owner) and `blocked` (stuck on something outside the agent's control).

## Create

Bash / Git Bash / zsh:

```sh
mkdir -p ~/.orca/tickets
python -c "import sqlite3,os;d=os.path.expanduser('~/.orca/tickets/tickets.db');sqlite3.connect(d).executescript(open('db/schema.sql').read())"
```

Seed the machine defaults (adjust to your harnesses):

```sh
python -c "import sqlite3,os;c=sqlite3.connect(os.path.expanduser('~/.orca/tickets/tickets.db'));c.executemany('INSERT OR REPLACE INTO repo_config VALUES (?,?,?,?,?,?)',[('*','manager','claude','sonnet-5.5','low','orca'),('*','worker','omp','deepseek-4.1','low','orca'),('*','reviewer','commandcode','glm-5.3-flash',None,'headless')]);c.commit()"
```

## Query templates

Each one-liner opens the db, runs one statement, prints rows, commits. Replace the `<…>` values.
A tiny helper keeps them short; define it once per shell if you like:

```sh
DB='import sqlite3,os,sys;c=sqlite3.connect(os.path.expanduser("~/.orca/tickets/tickets.db"));c.row_factory=sqlite3.Row'
```

```sh
# config for a repo (repo row wins over '*')
python -c "$DB;[print(dict(r)) for r in c.execute('SELECT * FROM repo_config WHERE repo IN (?,\"*\") ORDER BY repo=\"*\"',(sys.argv[1],))]" <repo>

# new ticket, prints its id
python -c "$DB;cur=c.execute('INSERT INTO tickets(repo,story,title,goal,acceptance,verify,scope) VALUES (?,?,?,?,?,?,?)',sys.argv[1:8]);c.commit();print(cur.lastrowid)" <repo> <story> "<title>" "<goal>" "<acceptance>" "<verify>" "<scope>"

# open tickets in a repo
python -c "$DB;[print(dict(r)) for r in c.execute('SELECT id,story,title,status,branch,fix_rounds FROM tickets WHERE repo=? AND status<>\"done\"',(sys.argv[1],))]" <repo>

# one ticket in full
python -c "$DB;print(dict(c.execute('SELECT * FROM tickets WHERE id=?',(sys.argv[1],)).fetchone()))" <id>

# move status (stamps started/review/done)
python -c "$DB;s,i=sys.argv[1:3];col={'in-progress':'started_at','review':'review_at','done':'done_at'}.get(s);c.execute('UPDATE tickets SET status=?'+(f',{col}=datetime(\"now\")' if col else '')+' WHERE id=?',(s,i));c.commit()" review <id>

# count a FIX round
python -c "$DB;c.execute('UPDATE tickets SET fix_rounds=fix_rounds+1 WHERE id=?',(sys.argv[1],));c.commit()" <id>

# start / end a run
python -c "$DB;cur=c.execute('INSERT INTO runs(ticket,role,harness,model,effort,mode) VALUES (?,?,?,?,?,?)',sys.argv[1:7]);c.commit();print(cur.lastrowid)" <id> worker omp deepseek-4.1 low orca
python -c "$DB;c.execute('UPDATE runs SET ended=datetime(\"now\"),result=? WHERE id=?',sys.argv[1:3]);c.commit()" PASS <run_id>

# story board across repos
python -c "$DB;[print(dict(r)) for r in c.execute('SELECT repo,id,title,status,pr_url FROM tickets WHERE story=? ORDER BY repo,id',(sys.argv[1],))]" S-12
```

Pass values as `sys.argv` (never paste them into the SQL string) so quotes in titles can't break or inject anything.

## Windows PowerShell

The `$DB` variable above is a bash convenience. In PowerShell, put the Python in single quotes, use double quotes inside it, and write SQL string literals as doubled single quotes (`''done''`):

```powershell
python -c 'import sqlite3,os,sys;c=sqlite3.connect(os.path.expanduser("~/.orca/tickets/tickets.db"));[print(r) for r in c.execute("SELECT id,title,status FROM tickets WHERE repo=? AND status<>''done''",(sys.argv[1],))]' C:\code\myrepo
```

Windows PowerShell 5.1 can still mangle embedded double quotes when calling native programs. If a one-liner misbehaves, write it to a `.py` file in a temp dir and run `python q.py <args>` instead.
