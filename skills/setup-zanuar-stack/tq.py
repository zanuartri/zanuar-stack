#!/usr/bin/env python3
"""Run one SQL statement on the ticket db.

python3 tq.py sql "<SQL with ? placeholders>" [params...]
python3 tq.py --file query.sql --params-file params.json
Use - as a filename to read SQL or JSON from stdin. Use - as a positional
parameter for SQL NULL. Results are JSON lines, an insert id, or a row count.
"""
import argparse
import json
import sys
from pathlib import Path

from init_db import connect


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
