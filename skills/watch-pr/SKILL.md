---
name: watch-pr
description: Own a pull request through CI and review, or write attributed GitHub PR comments. Use when asked to watch, babysit, or own a PR, or when posting a PR comment or reply.
---

# Watch PR

## Waiting, without polling yourself
GitHub can't reach this machine without a public endpoint, so something has to poll. Let one cheap local process do it and sleep until it mails you:

```sh
python3 "$watch_pr_dir/pr_watch.py" &   # watch_pr_dir is the directory containing this skill
```

- It watches every ticket in the db that has a `pr_url` and is neither `done` nor `canceled`, one machine-wide process for all repos (lock file next to `tickets.db`). In lite mode, use `gh pr checks <n> --watch` and inspect PR comments with `gh pr view <n> --comments`.
- Each tick is **one** `gh api graphql` call for all PRs (about 1 point of the 5000/hour GraphQL budget). 30s while checks are pending or a PR changed in the last 10 min, backing off to 5 min when idle; it sleeps until reset if the rate limit runs low, and exits when no open PR is left.
- On a change it sends one message to the ticket's `manager_dispatch`: subject `PR <repo>#<n>: <events>`, body the PR URL and current facts. Events: `ci_passed`, `ci_failed`, `conflicted`, `changes requested`, `new review`, `new comment`, `new commits by <someone else>`, `merged`, `closed`. Repos without CI only get the non-CI events.
- Save the active manager dispatch on each ticket before starting the watcher. Refresh it from the new task preamble whenever a follow-up wakes the manager. Senders must also update changed dispatch IDs as described in the Orca adapter.
- `python3 pr_watch.py --self-test` checks the diff logic with no network.
- Your own PR comments also wake you once; ignore those.

Optional, with Orca Cloud: an Orca automation on the PR's `github.*` events that messages your session does the same job without the local process. Remove it when the PR is ready.

Without Orca: one blocking `gh pr checks <pr> --watch` in the background, re-run after each event.

## On each wake-up
1. Read the new state: `gh pr checks <pr>`, `gh pr view <pr> --comments`, review threads.
2. **Failed check**: read the log, trace the failure to its cause, fix on the branch (through the worker if one is still open), and push. After 2 failed attempts, escalate with what you tried.
3. **Review comment** (human or bot): fix real issues and explain any feedback you decline. Follow [Writing PR comments](#writing-pr-comments).
4. **Conflict**: rebase or merge the base into the branch, re-run verify, push.
5. **ci_passed**: confirm the live PR head has been reviewed and verify required checks and review threads on that head. Apply the **manager** skill's merge approval rule to the live target branch, or report the PR ready for approval.
6. **merged / closed**: set the ticket `done` (or `blocked` if closed unmerged) and report.

## Stop
Stop when required checks are green and no threads are open, or when you need the owner. The watcher stops on its own once no open PR remains. Report: PR link, check state, what you changed.

Only the session that owns the PR watches it; delegated helpers don't.

## Writing PR comments

Start agent-written comments and replies with this attribution, including inline review comments. Use the reported model or fall back to the harness name. Preserve text the owner asks you to post verbatim.

```md
> [!NOTE]
> 🤖 **<model or harness> replying for <owner>**

The actual comment.
```

Lead with the conclusion and cite the code, check or reproduction. Distinguish verified facts from judgment. Scan the comment and attachments for private details, preview the Markdown, and confirm the comment URL after posting. Resolve a thread only after the reply posts.
