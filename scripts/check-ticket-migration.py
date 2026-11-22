"""Exercise the status upgrade on a populated pre-upgrade database."""

import os
from pathlib import Path
import sqlite3
import sys
from tempfile import TemporaryDirectory


setup = Path(__file__).resolve().parents[1] / "skills" / "setup-zanuar-stack"
sys.path.insert(0, str(setup))

with TemporaryDirectory() as temp:
    db = Path(temp) / "legacy.db"
    os.environ["ZANUAR_DB"] = str(db)
    from init_db import connect

    schema = (setup / "schema.sql").read_text(encoding="utf-8")
    legacy = schema.replace("'todo','queued',", "'todo',").replace("'done','canceled'", "'done'")
    with sqlite3.connect(db) as connection:
        connection.executescript(legacy)
        connection.execute("INSERT INTO stories VALUES ('S-1', 'Legacy story')")
        connection.execute(
            "INSERT INTO tickets(id, repo, story, title, status, fix_rounds) "
            "VALUES (3, 'repo', 'S-1', 'Review this', 'review', 2), "
            "(9, 'repo', 'S-1', 'Deleted ticket', 'done', 0)"
        )
        connection.execute("DELETE FROM tickets WHERE id=9")
        connection.execute(
            "INSERT INTO runs(ticket, role, harness, mode) VALUES (3, 'worker', 'codex', 'headless')"
        )
        connection.execute("INSERT INTO decisions(ticket, decision) VALUES (3, 'Keep history')")
    connection.close()

    with connect() as connection:
        assert connection.execute("SELECT status, fix_rounds FROM tickets WHERE id=3").fetchone() == (
            "review", 2
        )
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        assert "tickets_repo_status" in {row[1] for row in connection.execute("PRAGMA index_list(tickets)")}
        queued = connection.execute(
            "INSERT INTO tickets(repo, title, status, depends_on) VALUES ('repo', 'Waiting', 'queued', '3')"
        ).lastrowid
        assert queued == 10
        connection.execute("UPDATE tickets SET status='canceled' WHERE id=?", (queued,))
    connection.close()

    with connect() as connection:
        assert connection.execute("SELECT status FROM tickets WHERE id=?", (queued,)).fetchone() == (
            "canceled",
        )
        try:
            connection.execute("UPDATE tickets SET status='unknown' WHERE id=?", (queued,))
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("Invalid ticket status accepted")
    connection.close()

print("Ticket status migration checks passed")
