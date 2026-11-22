---
name: comment-sweep
description: Sweep a diff for comments that don't earn their place, delete them, fix the workarounds they excuse, and turn "do not remove" warnings into real checks. Use before a worker reports done, when a reviewer checks a branch, or when the owner says comment sweep or "clean up the comments".
---

# Comment sweep

Comments rot. Code that needs prose to be safe usually needs a better shape instead.

## Scope

The files or diff you were given. Otherwise the branch's diff against its base (default `main`), including uncommitted changes.

## Steps

1. **Fresh pass.** If the harness can start a subagent, give it the scope and the rules below and ask for a report only, no edits. Otherwise do one fresh read of the scope yourself, judging only comments.
2. **Delete** a comment when it:
   - restates what the code already says (narration, banners, section labels)
   - is stale: describes code that no longer looks or behaves that way
   - is commented-out code
   - excuses a workaround ("hack", "fine for now", "too risky to touch"). Delete it and fix the root cause instead (**root-cause**), as long as the fix stays inside the ticket's scope. Out of scope: land the smallest in-scope fix and report the rest open.
   - explains a surprise in *our own* code. Rename, extract or retype until the surprise is gone.
3. **Keep** only comments about things we cannot change:
   - license or legal headers
   - a rule forced by a dependency, platform, vendor or protocol, proven true from its docs or source; if you can't check it, keep it and flag it `REVIEW` with the rule it claims
   - doc comments that define a public API contract
   - issue or RFC links for a constraint the code can't express
   - lint suppressions, only when the rule is wrong or purely stylistic. A suppression that hides a real bug is a defect: fix the code.

   When unsure whether a keep applies, delete.
4. **Constraint comments** ("do not remove", "do not change this wording", "ask X before changing"): offer the cheapest enforcement instead, a type, a test or a lint rule, and delete the comment once it's encoded. Without approval, delete it and report the constraint as open.
5. **Never change application behavior** beyond the accepted fixes from steps 2 and 4. No drive-by refactors.
6. **Report**: deletions (count), `REVIEW` keeps, root-cause fixes made, enforcement offered or added, and what is still open.

## Examples

- Web app: `// fetch the user` above `fetchUser()` → delete. `// don't remove: layout breaks without this wrapper` → a render test that fails without it.
- CLI: `# exit 0 even on error because CI is flaky` → delete, return the real exit code, fix or report the flaky caller.
- Service: `// upstream returns 503 on cold start, retry 3 times (vendor docs)` → keep if the docs say so, else `REVIEW`.

## Who uses it

- **worker**: runs it on its own diff before reporting done.
- **reviewer**: checks the diff has no narration, stale notes or excused workarounds left; leftovers are FIX findings.
