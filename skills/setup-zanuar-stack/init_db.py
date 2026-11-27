#!/usr/bin/env python3
"""Create the zanuar-stack ticket db and write repo_config rows.

python3 init_db.py                         create ~/.orca/tickets/tickets.db (idempotent), print its path
python3 init_db.py detect                  list harness binaries and existing skills directories
python3 init_db.py set <repo> <role> <harness> <model> <effort> <mode>
python3 init_db.py show [repo]             print repo_config and repo_settings rows
python3 init_db.py settings <repo> <ask|review|merge> <pr|local>   autonomy and land for a repo (or *)
python3 init_db.py base <repo> <branch|->   integration branch, or - for the GitHub default
Use - for a model/effort the harness doesn't take (PowerShell 5.1 drops "" arguments).
"""
import os, shutil, sqlite3, sys
from pathlib import Path

DB = os.path.expanduser(os.environ.get("ZANUAR_DB", "~/.orca/tickets/tickets.db"))
SCHEMA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
# Columns added after v0. CREATE TABLE IF NOT EXISTS skips existing tables, so add them here.
TICKET_COLUMNS = {
    "autonomy": "TEXT CHECK (autonomy IN ('ask','review','merge'))",
    "land": "TEXT CHECK (land IN ('pr','local'))",
    "manager_dispatch": "TEXT",
    "depends_on": "TEXT",
    "roles": "TEXT",
    "base": "TEXT",
}
STORY_COLUMNS = {"feature_id": "TEXT REFERENCES features(id)"}


def migrate_ticket_statuses(c):
    ddl, = c.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='tickets'"
    ).fetchone()
    old_check = "CHECK (status IN ('todo','in-progress','review','needs-you','blocked','done'))"
    if old_check not in ddl:
        return

    # Rebuild in the setup transaction without renaming the referenced table.
    # SQLite connections here leave foreign key enforcement off during the copy.
    new_check = "CHECK (status IN ('todo','queued','in-progress','review','needs-you','blocked','done','canceled'))"
    objects = c.execute(
        "SELECT sql FROM sqlite_master WHERE tbl_name='tickets' "
        "AND type IN ('index','trigger') AND sql IS NOT NULL"
    ).fetchall()
    sequence = c.execute("SELECT seq FROM sqlite_sequence WHERE name='tickets'").fetchone()
    _, _, columns = ddl.partition("(")
    c.execute("CREATE TABLE tickets_new (" + columns.replace(old_check, new_check, 1))
    c.execute("INSERT INTO tickets_new SELECT * FROM tickets")
    c.execute("DROP TABLE tickets")
    c.execute("ALTER TABLE tickets_new RENAME TO tickets")
    for sql, in objects:
        c.execute(sql)
    if sequence:
        c.execute("DELETE FROM sqlite_sequence WHERE name='tickets'")
        c.execute("INSERT INTO sqlite_sequence(name, seq) VALUES ('tickets', ?)", sequence)


def connect():
    Path(DB).parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB)
    with open(SCHEMA, encoding="utf-8") as f:
        c.executescript(f.read())
    with c:
        c.execute("BEGIN IMMEDIATE")
        have = {r[1] for r in c.execute("PRAGMA table_info(tickets)")}
        for col, decl in TICKET_COLUMNS.items():
            if col not in have:
                c.execute(f"ALTER TABLE tickets ADD COLUMN {col} {decl}")
        have = {r[1] for r in c.execute("PRAGMA table_info(stories)")}
        for col, decl in STORY_COLUMNS.items():
            if col not in have:
                c.execute(f"ALTER TABLE stories ADD COLUMN {col} {decl}")
        migrate_ticket_statuses(c)
        if "base" not in {r[1] for r in c.execute("PRAGMA table_info(repo_settings)")}:
            c.execute("ALTER TABLE repo_settings ADD COLUMN base TEXT")
    return c


def detect():
    for harness in ("claude", "codex", "omp", "commandcode", "opencode", "pi"):
        if binary := shutil.which(harness):
            print(f"{harness}: {binary}")
    for entry in ("~/.claude/skills", "~/.codex/skills", "~/.omp/agent/skills",
                  "~/.commandcode/skills", "~/.config/opencode/skills", "~/.agents/skills"):
        path = Path(entry).expanduser()
        if path.is_dir():
            print(f"skills: {path}")


def main(argv):
    if argv == ["detect"]:
        detect()
        return
    c = connect()
    if argv[:1] == ["set"] and len(argv) == 7:
        _, repo, role, harness, model, effort, mode = argv
        c.execute("INSERT OR REPLACE INTO repo_config VALUES (?,?,?,?,?,?)",
                  (repo, role, harness, None if model == "-" else model,
                   None if effort == "-" else effort, mode))
        c.commit()
    elif argv[:1] == ["settings"] and len(argv) == 4:
        c.execute("""
            INSERT INTO repo_settings(repo, autonomy, land) VALUES (?,?,?)
            ON CONFLICT(repo) DO UPDATE SET autonomy=excluded.autonomy, land=excluded.land
        """, tuple(argv[1:]))
        c.commit()
    elif argv[:1] == ["base"] and len(argv) == 3 and argv[1] != "*":
        _, repo, base = argv
        c.execute("""
            INSERT INTO repo_settings(repo, autonomy, land, base)
            SELECT ?, autonomy, land, ? FROM repo_settings WHERE repo='*'
            ON CONFLICT(repo) DO UPDATE SET base=excluded.base
        """, (repo, None if base == "-" else base))
        c.commit()
    elif argv[:1] == ["show"]:
        q, args = "SELECT * FROM repo_config", ()
        if len(argv) > 1:
            q, args = q + " WHERE repo IN (?, '*')", (argv[1],)
        for row in c.execute(q + " ORDER BY repo, role", args):
            print(row)
        for row in c.execute(q.replace("repo_config", "repo_settings") + " ORDER BY repo", args):
            print(row)
        return
    elif argv:
        sys.exit(__doc__)
    print(DB)


if __name__ == "__main__":
    main(sys.argv[1:])
