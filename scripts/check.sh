#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
check_dir=$(mktemp -d)
trap 'rm -rf "$check_dir"' EXIT
check_home="$check_dir"
case "$(uname -s)" in
    MINGW*|MSYS*) check_home=$(cygpath -am "$check_dir") ;;
esac

unset ZANUAR_DB
export LC_ALL=C LANG=C TZ=UTC PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1
run_python() {
    env HOME="$check_home" USERPROFILE="$check_home" python3 "$@"
}

setup=skills/setup-zanuar-stack
run_python "$setup/init_db.py"
test -f "$check_dir/.orca/tickets/tickets.db"
run_python "$setup/init_db.py" set '*' worker codex - - orca
run_python "$setup/init_db.py" show
run_python "$setup/init_db.py" detect
run_python skills/watch-pr/pr_watch.py --self-test
run_python skills/watch-pr/pr_watch.py

printf 'INSERT INTO tickets(repo, title, goal)\nVALUES (?, ?, ?)\n' > "$check_dir/insert.sql"
printf '%s\n' '["example", "Café", "First line\nSecond line"]' > "$check_dir/ticket.json"
test "$(run_python "$setup/tq.py" --file "$check_dir/insert.sql" --params-file "$check_dir/ticket.json" | tr -d '\r')" = 1

printf 'SELECT title, goal\nFROM tickets WHERE id=?\n' > "$check_dir/select.sql"
expected='{"title": "Café", "goal": "First line\nSecond line"}'
test "$(printf '[1]\n' | run_python "$setup/tq.py" --file "$check_dir/select.sql" --params-file - | tr -d '\r')" = "$expected"
test "$(run_python "$setup/tq.py" --file - 1 < "$check_dir/select.sql" | tr -d '\r')" = "$expected"
test "$(run_python "$setup/tq.py" sql 'SELECT goal FROM tickets WHERE id=?' 1 | tr -d '\r')" = '{"goal": "First line\nSecond line"}'
printf '%s\n' 'Ticket database and PR watcher checks passed'

run_python "$setup/init_db.py" set '*' worker codex default-model medium orca
test "$(run_python "$setup/tq.py" resolve-role 1 worker | tr -d '\r')" = '{"harness": "codex", "model": "default-model", "effort": "medium", "mode": "orca"}'
run_python "$setup/init_db.py" set example worker codex repo-model - headless
test "$(run_python "$setup/tq.py" resolve-role 1 worker | tr -d '\r')" = '{"harness": "codex", "model": "repo-model", "effort": "medium", "mode": "headless"}'
printf '%s\n' '["{\"worker\":{\"harness\":\"claude\",\"model\":\"ticket-model\"}}", 1]' > "$check_dir/roles.json"
printf '%s\n' "UPDATE tickets SET roles=json_patch(coalesce(roles, '{}'), json(?)) WHERE id=?" > "$check_dir/roles.sql"
run_python "$setup/tq.py" --file "$check_dir/roles.sql" --params-file "$check_dir/roles.json"
test "$(run_python "$setup/tq.py" resolve-role 1 worker | tr -d '\r')" = '{"harness": "claude", "model": "ticket-model", "effort": "medium", "mode": "headless"}'
printf '%s\n' 'Ticket role resolution check passed'

test "$(run_python "$setup/tq.py" resolve-base 1 main | tr -d '\r')" = main
run_python "$setup/init_db.py" base example develop
run_python "$setup/init_db.py" settings example merge pr
test "$(run_python "$setup/tq.py" resolve-base 1 main | tr -d '\r')" = develop
run_python "$setup/tq.py" sql 'UPDATE tickets SET base=? WHERE id=?' main 1
test "$(run_python "$setup/tq.py" resolve-base 1 trunk | tr -d '\r')" = main
run_python "$setup/tq.py" sql 'UPDATE tickets SET base=NULL WHERE id=?' 1
run_python "$setup/init_db.py" base example -
test "$(run_python "$setup/tq.py" resolve-base 1 trunk | tr -d '\r')" = trunk
printf '%s\n' 'Ticket base resolution check passed'
