# Working across Orca bots

Run `orca bot list` to find bots on this computer, see what each handles, and get its address. Use that address in `orca orchestration send`.

| Purpose | Command |
|---|---|
| Ask for input | `orca orchestration send --to bot:<recipient> --type question --subject "Review draft" --body-file question.md` |
| Hand over work | `orca orchestration send --to bot:<recipient> --type handoff --chat new --subject "Take over the task" --body-file handoff.md` |
| Share news | `orca orchestration send --to bot:<recipient> --type status --subject "Task ready" --body-file status.md` |

Mail goes to the bot's Home Chat by default. Use `--chat new` with a handoff or question to open a separate chat. Answers return as mail to the sender and are available through `orca orchestration check`. The owner sees bot answers on cards in Orca.

Any bot can ask, hand over work, or share news. Name the format in every handoff and follow its skill or heading list. Bring the owner in for decisions that require the owner.

## Example 1 — Design handoff and review

Use [design-handoff](../../skills/design-handoff/SKILL.md) to request design or pass an approved design to implementation.

To request design review, send the PR link, the handoff, and screenshots of each required state from the [make-verify](../../skills/make-verify/SKILL.md) recipe. Capture proof at the PR revision under review. Compare it with the handoff's acceptance checks and reply **PASS** or **FIX**. For each FIX, give the screen, state, expected result, and actual result or missing screenshot.

Other teams add their own handoff format the same way. Name a skill or agree on headings, then reference that format when sending the handoff.
