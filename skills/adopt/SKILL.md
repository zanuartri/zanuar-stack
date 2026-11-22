---
name: adopt
description: Take over existing work (a PR, branch, ticket or another agent's session) and finish its original goal while keeping the original authors' credit. Use when the owner says adopt, take over, pick up this PR, or finish what another agent started.
---

# Adopt

You now own the goal, not the previous implementation. Don't defend code just because it exists.

1. **Read everything**: the PR or branch, its review comments, the ticket and its runs, the owner's later corrections. Check the real head and any uncommitted work. The handoff note is a hint, not proof.
2. **Pick the shape**: by default, a new branch with the original commits, your fixes as separate commits on top. Continue in place or stack only when asked. Don't rewrite someone else's PR without permission.
3. **Keep credit**: preserve git authorship and `Co-authored-by` trailers. Name the original contributors and link the original PR in the description. When squashing, keep human co-authors in the squash message, using identities you verified, never guessed emails. Model attribution doesn't replace human credit.
4. **Finish the same goal**: rebase onto the current base, rework only what the goal needs, simplify without dropping intended behaviour. Re-check the original PR before you finish; it may have moved.
5. **Verify independently**: reproduce the original problem and the real workflow. Green mocks are not proof. Say what is still unverified.
6. **Land**: **open-pr**, then **watch-pr**. Close or merge the original only when authorized.
7. In the db, set yourself as the owner of the ticket (or create one) and log the handoff in `runs`.

Report: what you inherited, what you changed, how you verified it, how credit was kept, and what decision is left.
