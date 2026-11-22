# Feature recipe template

Copy to `verify/<feature>.md` and fill every section from the real repo. Leave no placeholders.

```markdown
# <Feature name>

What it is, in one or two lines, from the user's point of view.

## Preconditions
- App launched per verify/README.md, from a fresh data dir.
- Seed data or state this feature needs (one existing record, a test account).

## Steps
1. <user action with a stable handle: route, button label, command, endpoint>
2. ...

## Expected result
What the user sees, and what is stored, when it works.

## Proof to capture
- <what to save, and where in the evidence folder>

## Gotchas
Known traps: slow first start, missing seed, OS-specific flags.
```

## Examples

**Web app: create a note**
- Steps: open `/notes`, click "New note", type a title, press Save.
- Expected: the note is at the top of the list and survives a reload.
- Proof: a screenshot or accessibility snapshot after Save and after the reload.

**CLI: export**
- Steps: `<tool> export --out <tmpdir>/out.csv` against the seeded data dir.
- Expected: exit code 0, one line per seeded record, nothing on stderr.
- Proof: the command, stdout, stderr, exit code, and the first lines of the output file.

**Service: create an order**
- Steps: `POST /orders` with a test payload to the local instance.
- Expected: `201` with an id; a following `GET /orders/<id>` returns the same data.
- Proof: request and response bodies, then the second read of stored state (the GET, or a query on the throwaway DB).
