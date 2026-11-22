---
name: watch-pr
description: Own a pull request through CI and review until it is ready, fixing what is asked. Use when the owner says watch, babysit, or own the PR, or after open-pr when the ticket asks for it.
---

# Watch PR

## Waiting, without polling
Never write your own `sleep` loop or watcher. Pick one wake-up source per PR:
- **Orca**: create an automation on the `github.ci_*` events (and review/comment events if available) for this PR that messages your session, then end your turn. You'll be woken when something happens.
- **Elsewhere**: one blocking `gh pr checks <pr> --watch` run in the background, re-run after you handle each event.

All watchers on a GitHub account share one rate limit. If reads start failing, check `gh api rate_limit --jq .resources.graphql` and wait for `reset` once.

## On each wake-up
1. Read the new state: `gh pr checks <pr>`, `gh pr view <pr> --comments`, review threads.
2. **Failed check**: read the log, find the root cause (**root-cause**), fix on the branch, push the branch.
3. **Review comment** (human or bot): bots are useful but not always right. Fix real issues; for the rest, reply why (**pr-comments**). Resolve a thread only after your reply posted.
4. **Conflict**: rebase or merge the base into the branch, re-run verify, push.
5. A wake-up is news, not a merge decision.

## Stop
Stop when required checks are green and no threads are open, or when you need the owner. Remove your automation/watcher first. Report: PR link, check state, what you changed. Merge only with the owner's explicit OK.

Only the session that owns the PR watches it; delegated helpers don't.
