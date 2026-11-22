# Working across Orca bots

Run `orca bot list` to find bots on this computer, see what each handles, and get its address. Use that address in `orca orchestration send`.

| Purpose | Command |
|---|---|
| Ask for input | `orca orchestration send --to bot:<name> --type question --subject "Review PR UI" --body-file review.md` |
| Hand over a job | `orca orchestration send --to bot:<name> --type handoff --chat new --subject "Implement the design" --body-file handoff.md` |
| Share news | `orca orchestration send --to bot:<name> --type status --subject "Design approved" --body "The design is ready."` |

Mail goes to the bot's Home Chat by default. Use `--chat new` with a handoff or question to open a separate chat. Answers return as mail to the sender and are available through `orca orchestration check`. The owner sees bot answers on cards in Orca.

- The design lead sends a [design handoff](../../skills/design-handoff/SKILL.md) to the engineering orchestrator, who uses it to write the story and briefs. Engineering can request design using the same headings.
- The engineering orchestrator or manager asks the design lead for a [UI review](../../skills/ui-review/SKILL.md) when a ticket changes user-facing UI and the design lead is available. Send the PR, handoff, and screenshot links or the recipe to capture them.
- Bots send questions, handoffs, and verdicts directly to each other. Bring the owner in for decisions that require the owner.
