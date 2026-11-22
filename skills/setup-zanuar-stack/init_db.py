"""Create the zanuar-stack ticket db and write repo_config rows.

python init_db.py                         create ~/.orca/tickets/tickets.db (idempotent), print its path
python init_db.py set <repo> <role> <harness> <model> <effort> <mode>
python init_db.py show [repo]             print repo_config rows
Use - for a model/effort the harness doesn't take (PowerShell 5.1 drops "" arguments).
"""
import os, sqlite3, sys

DB = os.path.expanduser(os.environ.get("ZANUAR_DB", "~/.orca/tickets/tickets.db"))
SCHEMA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")


def connect():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    c = sqlite3.connect(DB)
    with open(SCHEMA, encoding="utf-8") as f:
        c.executescript(f.read())
    return c


def main(argv):
    c = connect()
    if argv[:1] == ["set"] and len(argv) == 7:
        _, repo, role, harness, model, effort, mode = argv
        c.execute("INSERT OR REPLACE INTO repo_config VALUES (?,?,?,?,?,?)",
                  (repo, role, harness, None if model == "-" else model,
                   None if effort == "-" else effort, mode))
        c.commit()
    elif argv[:1] == ["show"]:
        q, args = "SELECT * FROM repo_config", ()
        if len(argv) > 1:
            q, args = q + " WHERE repo IN (?, '*')", (argv[1],)
        for row in c.execute(q + " ORDER BY repo, role", args):
            print(row)
        return
    elif argv:
        sys.exit(__doc__)
    print(DB)


if __name__ == "__main__":
    main(sys.argv[1:])
