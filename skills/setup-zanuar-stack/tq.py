#!/usr/bin/env python3
"""Run one SQL statement on the ticket db.

python3 tq.py sql "<SQL with ? placeholders>" [params...]
python3 tq.py --file query.sql --params-file params.json
python3 tq.py resolve-role <ticket> <worker|reviewer>
Use - as a filename to read SQL or JSON from stdin. Use - as a positional
parameter for SQL NULL. Results are JSON lines, an insert id, or a row count.
"""
import argparse
import json
import sys
from pathlib import Path

from init_db import connect


def resolve_role(ticket, role):
    with connect() as c:
        row = c.execute("""
            WITH dispatch AS (
                SELECT repo, json_extract(roles, '$.' || :role) AS overrides
                FROM tickets WHERE id = :ticket
            )
            SELECT
                coalesce(json_extract(overrides, '$.harness'), local.harness, defaults.harness),
                coalesce(json_extract(overrides, '$.model'), local.model, defaults.model),
                coalesce(json_extract(overrides, '$.effort'), local.effort, defaults.effort),
                coalesce(json_extract(overrides, '$.mode'), local.mode, defaults.mode)
            FROM dispatch
            LEFT JOIN repo_config AS local ON local.repo = dispatch.repo AND local.role = :role
            LEFT JOIN repo_config AS defaults ON defaults.repo = '*' AND defaults.role = :role
        """, {"ticket": ticket, "role": role}).fetchone()
    if row is None:
        sys.exit(f"Unknown ticket: {ticket}")
    print(json.dumps(dict(zip(("harness", "model", "effort", "mode"), row)), ensure_ascii=False))


def read_text(filename):
    if filename == "-":
        return sys.stdin.buffer.read().decode("utf-8-sig")
    return Path(filename).read_text(encoding="utf-8-sig")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", metavar="SQL_FILE")
    parser.add_argument("--params-file", metavar="JSON_FILE")
    parser.add_argument("args", nargs="*")
    argv = sys.argv[1:]
    if argv[:1] == ["resolve-role"]:
        if len(argv) != 3 or argv[2] not in ("worker", "reviewer"):
            parser.error("use resolve-role TICKET worker|reviewer")
        resolve_role(argv[1], argv[2])
        return
    args = parser.parse_args(["--", *argv] if argv[:1] == ["sql"] else argv)
    if args.file is None:
        if len(args.args) < 2 or args.args[0] != "sql":
            parser.error("use sql STATEMENT or --file SQL_FILE")
        _, sql, *params = args.args
    else:
        if args.file == args.params_file == "-":
            parser.error("only one input can read from stdin")
        sql, params = read_text(args.file), args.args
    if args.params_file is None:
        params = [None if param == "-" else param for param in params]
    else:
        if params:
            parser.error("choose positional parameters or --params-file")
        try:
            params = json.loads(read_text(args.params_file))
        except ValueError as exc:
            parser.error(str(exc))
        if not isinstance(params, (list, dict)):
            parser.error("JSON parameters must be an array or object")

    with connect() as c:
        cur = c.execute(sql, params)
        if cur.description:
            cols = [column[0] for column in cur.description]
            for row in cur:
                print(json.dumps(dict(zip(cols, row)), ensure_ascii=False))
            return
        c.commit()
        print(cur.lastrowid if sql.lstrip().upper().startswith("INSERT") else cur.rowcount)


if __name__ == "__main__":
    main()
