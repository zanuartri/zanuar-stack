---
name: open-pr
description: Open a short, readable pull request for a finished ticket branch. Use when the manager lands a ticket, or the owner says open a PR, file a PR, or create a PR.
---

# Open PR

1. **Already one?** `gh pr list --head <branch>`. If so, update it instead.
2. **Check the diff** against the base (`git diff origin/<base>...HEAD --stat`, then the full diff if you are the one reading code). It must match the ticket's goal, nothing extra.
3. **Title**: follow the repo's convention (look at recent merged PRs). Say why it matters, not which mechanism changed.
   - weak: `refactor(api): add cache layer to user lookup`
   - better: `perf(api): user page loads 3x faster`
4. **Body**: open with the problem in plain words, from the owner's point of view, then the fix in a sentence or two. Then verify output and risks. Don't lead with a file inventory. Link the ticket/story.
5. End the body with the model and harness that wrote it (e.g. `Written by <model> in <harness>.`), plus any helper models. Don't guess a model name you can't see.
6. **Scan** title, body and attachments for secrets and private details.
7. Push the branch (never the base) and open a real PR, not a draft, so review bots run: `gh pr create --base <base> --head <branch> --title … --body-file …`. If GraphQL is rate-limited, use `gh api repos/<o>/<r>/pulls -f title=… -f head=… -f base=… -F body=@<file>`.
8. Save `pr_url` on the ticket. Continue with **watch-pr** if asked.

Don't add follow-up comments unless they serve the request; use **pr-comments** when you do.
