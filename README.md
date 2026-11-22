# zanuar-stack

A skill pack for running coding agents as a small team: one **lead** across repos, one **manager** per repo, and a **worker** plus **reviewer** per ticket. Built for [Orca](https://github.com/stablyai/orca) first, but the skills only assume a harness that can start another agent and pass messages, so they work elsewhere too.

```
                 owner
                   │  decisions only
                   ▼
                 lead ──── interview → story + one brief per repo
        ┌──────────┼──────────┐
        ▼          ▼          ▼
     manager    manager    manager      one per repo, kept open
      │    │
      ▼    ▼
   worker reviewer                      one ticket, own worktree/branch
      │    ▲
      └────┘  FIX rounds (max ~3) → PASS → PR
```

Shared state is one SQLite file, `~/.orca/tickets/tickets.db` (see [`db/`](db/README.md)): stories, tickets, runs, per-repo role config.

## Skills

| role skills | |
|---|---|
| [`lead`](skills/lead/SKILL.md) | cross-repo planning, briefs, escalation; never codes |
| [`manager`](skills/manager/SKILL.md) | tickets, dispatch, triage, review loop, PR |
| [`worker`](skills/worker/SKILL.md) | one ticket, verify, report |
| [`reviewer`](skills/reviewer/SKILL.md) | full-diff review, PASS or FIX |

| practice skills | |
|---|---|
| [`interview`](skills/interview/SKILL.md) | one-question-at-a-time requirements interview |
| [`big-plan`](skills/big-plan/SKILL.md) | design the workflow for large or unattended work |
| [`brief`](skills/brief/SKILL.md) | make a task deeper, then rewrite it |
| [`shape-first`](skills/shape-first/SKILL.md) | sketch types and boundaries before code |
| [`cut-first`](skills/cut-first/SKILL.md) | subtract before you add |
| [`root-cause`](skills/root-cause/SKILL.md) | fix where it first went wrong |
| [`test-first`](skills/test-first/SKILL.md) | failing regression test, then fix |
| [`ripple-check`](skills/ripple-check/SKILL.md) | what breaks outside the diff, proven |
| [`decision-log`](skills/decision-log/SKILL.md) | auditable trail in the db or a TSV |
| [`adopt`](skills/adopt/SKILL.md) | take over a PR or branch, keep credit |
| [`open-pr`](skills/open-pr/SKILL.md) | short, readable PRs |
| [`watch-pr`](skills/watch-pr/SKILL.md) | own a PR through CI and review |
| [`pr-comments`](skills/pr-comments/SKILL.md) | attributed, direct PR comments |

Harness wiring: [`adapters/orca`](adapters/orca/README.md).

## Install

Copy the skill folders into your agent's skills directory:

```sh
# Claude Code (user-wide)
cp -r skills/* ~/.claude/skills/
# other harnesses: copy skills/* into their skills dir
```

Create the db with the commands in [`db/README.md`](db/README.md). Then start a session with the `lead` skill (several repos) or the `manager` skill (one repo).

## Credits

The ideas here are adapted, in our own words, from:

- [herdr-rig](https://github.com/zanuartri/herdr-rig): the orchestrator / manager / worker / reviewer roles.
- Matt Pocock's "grill me" pattern: the `interview` skill.
- [backnotprop/pstack](https://github.com/backnotprop/pstack): `figure-it-out`, `sharpen`, `architect`, `show-me-your-work`, `tdd`, `principle-fix-root-causes`, `principle-subtract-before-you-add`, `blast-radius` → `big-plan`, `brief`, `shape-first`, `decision-log`, `test-first`, `root-cause`, `cut-first`, `ripple-check`.
- [t3dotgg/tstack](https://github.com/t3dotgg/tstack): `takeover`, `file-pr`, `babysit-pr`, `leaving-pr-comments` → `adopt`, `open-pr`, `watch-pr`, `pr-comments`.

## License

MIT, see [LICENSE](LICENSE).
