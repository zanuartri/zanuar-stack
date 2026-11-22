---
name: pr-comments
description: Write and post GitHub PR comments on the owner's behalf with clear agent attribution and a direct style. Use whenever an agent leaves a PR comment, review comment, or reply to a reviewer or bot.
---

# PR comments

## Attribution
Start every agent-written comment with a note callout, then the comment itself outside it:

```md
> [!NOTE]
> 🤖 **<model> replying for <owner>**

The actual comment.
```

- Use the model name the harness reports; if none, the harness name. Never guess.
- The context line starts with the robot emoji. No extra signatures, headings or rules.
- Applies to top-level comments, inline review comments, replies to bots and humans, and explanations before resolving feedback. Not to PR descriptions, commit messages, or text the owner asked to post verbatim.

## Style
- Conclusion first.
- Point at the code, check or repro that backs it.
- Short. No filler, canned thanks or status narration.
- Keep verified facts apart from opinion.

## Before and after posting
- Check the whole comment (quotes and attachments too) for secrets and private details.
- Preview the Markdown so quotes and blank lines render right.
- After posting, confirm GitHub returned a URL. Resolve a thread only after the reply is posted.
