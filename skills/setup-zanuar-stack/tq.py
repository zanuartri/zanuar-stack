"""Run one SQL statement on the ticket db without hand-quoting it in a shell.

python tq.py sql "<SQL with ? placeholders>" [params...]
Prints SELECT rows as JSON lines, or the new row id / changed row count, and commits.
Use - for a NULL param. Example:
python tq.py sql "UPDATE tickets SET branch=?, status='in-progress' WHERE id=?" zanuartri/t-12 12
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from init_db import connect

if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] != "sql":
        sys.exit(__doc__)
    c = connect()
    cur = c.execute(sys.argv[2], [None if p == "-" else p for p in sys.argv[3:]])
    if cur.description:
        cols = [d[0] for d in cur.description]
        for row in cur:
            print(json.dumps(dict(zip(cols, row)), ensure_ascii=False))
    else:
        c.commit()
        print(cur.lastrowid if sys.argv[2].lstrip().upper().startswith("INSERT") else cur.rowcount)
