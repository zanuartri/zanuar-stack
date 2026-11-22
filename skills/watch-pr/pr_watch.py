#!/usr/bin/env python3
"""Local PR watcher: one process per machine, polls GitHub, mails the owning manager on change.

python3 pr_watch.py              run until no open PR remains (second copy exits at once)
python3 pr_watch.py --self-test  check the diff logic, no network

Needs Python stdlib, `gh` (logged in) and `orca`. Reads tickets with pr_url from the ticket db,
fetches every PR in one `gh api graphql` call per tick, and sends one
`orca orchestration send --to dispatch:<tickets.manager_dispatch>` per PR that changed.
"""
import json, os, re, shutil, subprocess, sys, time
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "setup-zanuar-stack"))

FAST, SLOW, HOT = 30, 300, 600  # seconds: busy interval, idle ceiling, "recently changed" window
PR_RE = re.compile(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)")
PR_FIELDS = """state mergeable mergeStateStatus reviewDecision headRefOid
  commits(last:1){nodes{commit{statusCheckRollup{state} author{user{login}}}}}
  reviews(last:1){nodes{id state author{login}}}
  comments(last:1){nodes{id author{login}}}"""


def snapshot(pr):
    commit = pr["commits"]["nodes"][0]["commit"] if pr["commits"]["nodes"] else {}
    review = (pr["reviews"]["nodes"] or [None])[0]
    comment = (pr["comments"]["nodes"] or [None])[0]
    return {
        "state": pr["state"], "mergeable": pr["mergeable"], "merge_state": pr["mergeStateStatus"], "decision": pr["reviewDecision"],
        "head": pr["headRefOid"], "head_by": ((commit.get("author") or {}).get("user") or {}).get("login"),
        "checks": (commit.get("statusCheckRollup") or {}).get("state"),  # None = repo has no CI
        "review": review and review["id"], "review_state": review and review["state"],
        "review_by": review and (review["author"] or {}).get("login"),
        "comment": comment and comment["id"], "comment_by": comment and (comment["author"] or {}).get("login"),
    }


def diff(old, new, me):
    """Events between two snapshots. First sight (old None) reports only terminal CI, conflict, merged/closed."""
    if old is None:
        old = dict(new, checks=None, mergeable=None, state="OPEN")
    ev = []
    if new["state"] != old["state"] and new["state"] in ("MERGED", "CLOSED"):
        return [new["state"].lower()]
    if new["head"] != old["head"]:
        old = dict(old, checks=None)  # new commit: its checks start over
        if new["head_by"] and new["head_by"] != me:
            ev.append(f"new commits by {new['head_by']}")
    if new["checks"] != old["checks"]:
        if new["checks"] == "SUCCESS":
            ev.append("ci_passed")
        elif new["checks"] in ("FAILURE", "ERROR"):
            ev.append("ci_failed")
    if new["mergeable"] == "CONFLICTING" != old["mergeable"]:
        ev.append("conflicted")
    if new["review"] != old["review"] and new["review"]:
        ev.append("changes requested" if new["review_state"] == "CHANGES_REQUESTED"
                  else f"new review ({new['review_state'].lower()}) by {new['review_by']}")
    if new["comment"] != old["comment"] and new["comment"]:
        ev.append(f"new comment by {new['comment_by']}")
    return ev


def facts(s):
    return (f"state={s['state']} checks={s['checks'] or 'none'} mergeable={s['mergeable']}/{s['merge_state']} "
            f"review={s['decision'] or 'none'} head={s['head'][:8]}")


def gh_query(prs):
    parts = [f'p{i}: repository(owner:{json.dumps(o)}, name:{json.dumps(n)}){{pullRequest(number:{num}){{{PR_FIELDS}}}}}'
             for i, (o, n, num) in enumerate(prs)]
    q = "query{viewer{login} rateLimit{remaining resetAt} " + " ".join(parts) + "}"
    gh = shutil.which("gh")
    if not gh:
        sys.exit("pr_watch: gh not found on PATH")
    out = subprocess.run([gh, "api", "graphql", "-f", f"query={q}"],
                         capture_output=True, text=True, encoding="utf-8")
    if out.returncode:
        raise RuntimeError(out.stderr.strip()[:300])
    return json.loads(out.stdout)["data"]


def lock(path):
    f = open(path, "a+")
    f.seek(0)
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        sys.exit("pr_watch: already running")
    return f  # held until the process exits


def run():
    from init_db import DB, connect
    db_dir = os.path.dirname(os.path.abspath(DB))
    os.makedirs(db_dir, exist_ok=True)
    _lock = lock(os.path.join(db_dir, "pr_watch.lock"))
    c = connect()
    default_orca = "orca-ide" if sys.platform.startswith("linux") else "orca"
    orca = shutil.which(os.environ.get("ORCA_CLI_COMMAND") or default_orca)
    interval = FAST
    while True:
        rows = c.execute("SELECT t.pr_url, t.manager_dispatch, w.snapshot, w.updated_at FROM tickets t "
                         "LEFT JOIN pr_watch w ON w.pr_url = t.pr_url "
                         "WHERE t.pr_url IS NOT NULL AND t.status NOT IN ('done','canceled')").fetchall()
        watch = [(r, PR_RE.search(r[0])) for r in rows
                 if PR_RE.search(r[0]) and not (r[2] and json.loads(r[2])["state"] != "OPEN")]
        if not watch:
            print("pr_watch: no open PRs, exiting")
            return
        try:
            data = gh_query([m.groups() for _, m in watch])
        except Exception as e:  # network or auth hiccup: try again next tick
            print("pr_watch:", e, file=sys.stderr)
            time.sleep(interval)
            continue
        busy, now = False, time.time()
        for i, ((url, dispatch, old, updated), m) in enumerate(watch):
            pr = (data.get(f"p{i}") or {}).get("pullRequest")
            if not pr:
                continue
            new = snapshot(pr)
            events = diff(old and json.loads(old), new, data["viewer"]["login"])
            if events:
                subject = f"PR {m[2]}#{m[3]}: {', '.join(events)}"
                body = f"{url}\n{facts(new)}"
                if dispatch and orca:
                    subprocess.run([orca, "orchestration", "send", "--to", f"dispatch:{dispatch}",
                                    "--subject", subject, "--body", body])
                elif dispatch:
                    print("pr_watch: Orca CLI not found; set ORCA_CLI_COMMAND", file=sys.stderr)
                print(subject)
            if events or old is None:
                c.execute("INSERT OR REPLACE INTO pr_watch VALUES (?,?,datetime('now'))", (url, json.dumps(new)))
                c.commit()
                updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            recent = now - datetime.strptime(updated, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp() < HOT
            busy |= new["checks"] in ("PENDING", "EXPECTED") or recent
        interval = FAST if busy else min(interval * 2, SLOW)
        rl = data["rateLimit"]
        if rl["remaining"] < 50:
            reset = datetime.strptime(rl["resetAt"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
            interval = max(interval, reset - time.time() + 5)
        time.sleep(interval)


def self_test():
    base = {"state": "OPEN", "mergeable": "MERGEABLE", "merge_state": "CLEAN", "decision": None, "head": "a" * 40, "head_by": "me",
            "checks": "PENDING", "review": None, "review_state": None, "review_by": None,
            "comment": None, "comment_by": None}
    s = lambda **kw: dict(base, **kw)
    assert diff(None, base, "me") == []
    assert diff(None, s(checks="FAILURE"), "me") == ["ci_failed"]
    assert diff(base, base, "me") == []
    assert diff(base, s(checks="SUCCESS"), "me") == ["ci_passed"]
    assert diff(s(checks="FAILURE"), s(checks="FAILURE"), "me") == []
    assert diff(s(checks="SUCCESS"), s(checks="SUCCESS", head="b" * 40), "me") == ["ci_passed"]
    assert diff(base, s(head="b" * 40, head_by="bot"), "me") == ["new commits by bot"]
    assert diff(base, s(mergeable="CONFLICTING"), "me") == ["conflicted"]
    assert diff(base, s(review="R1", review_state="CHANGES_REQUESTED", review_by="x"), "me") == ["changes requested"]
    assert diff(base, s(comment="C1", comment_by="x"), "me") == ["new comment by x"]
    assert diff(base, s(state="MERGED", checks="SUCCESS"), "me") == ["merged"]
    assert diff(s(checks=None), s(checks=None, mergeable="UNKNOWN"), "me") == []  # no CI: quiet
    print("pr_watch self-test ok")


if __name__ == "__main__":
    self_test() if sys.argv[1:] == ["--self-test"] else run()
