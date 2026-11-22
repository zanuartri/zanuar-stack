---
name: make-verify
description: Build and maintain a repo-local verification map (verify/) that tells an agent how to launch the real app with disposable data, drive one user-facing feature, and capture proof. Use when a repo has no scripted way to prove user-facing behavior, when the owner says make verify or verification map, or when a reviewer needs to run a feature recipe.
---

# Make verify

Unit tests prove functions. A verify map proves the app does what a user sees. Write it for the next agent, who reads it cold, mid-task.

## Policy: optional

- The **reviewer** runs the matching feature recipe when the repo has `verify/` **and** the ticket changes user-facing behavior, or when the owner asks.
- Ordinary tickets stay **unit tests + typecheck + lint**.
- The **manager** creates the map, as its own ticket, when the owner asks or when user-facing tickets keep landing with no way to prove them.

## Safety, always

Never run against production or live systems, real money, wallets, payment providers or real credentials. Use local, sandbox or test-mode stand-ins only. **Never drive an instance this run didn't start**; stop only what you started, never by process name.

## 1. Read the repo, ask only what you can't see

- **Surface**: web UI, CLI, service/API, desktop, library? Pick the primary one, note the rest.
- **Run**: the repo's own start command, ports, env vars, seed data, auth.
- **Drive**: existing harnesses first (browser tests, scripts, HTTP calls), then a generic one: a browser for web, a shell or PTY for CLI, plain HTTP for services.
- **Observe**: screenshots, UI snapshots, stdout/stderr/exit codes, response bodies, stored state.
- **Isolate**: can a second copy run with its own port and data dir? If not, say so.

If the checkout doesn't start, fix that or report it precisely before writing the map.

## 2. Write `verify/README.md`

- **Launch**: exact command from an empty, disposable data dir (temp dir, throwaway DB, test config), including migrations and seed. Ready means usable, not just a port answering. Plus teardown.
- **Preconditions**: what must be true before driving (build done, deps installed, test keys set).
- **Health check**: one read-only check that this is the instance you started and it is worth driving.
- **Proof rules**: drive the real user path, not internal setters or test-only endpoints; capture the action *and* the resulting state; check side effects (files, rows, messages); trust a dry run only after observing what it skips.
- **Cleanup**: stop what you started, remove scratch data, keep the evidence in a named folder.
- **Index**: one line per feature file.

## 3. One file per feature

`verify/<feature>.md` for the top 3–5 user-facing features, shaped like [`references/feature-map.md`](references/feature-map.md): steps, expected result, proof to capture:
- web app: a UI snapshot or screenshot after the action
- CLI: the command, stdout, stderr and exit code
- service: the request and response, then a second read of stored state

If seed data lacks a precondition, the recipe fails and the reason goes in its Gotchas. Never weaken a recipe to make it pass.

## 4. Prove it once

Run the map end to end: launch, health check, drive ONE feature, capture proof, clean up, confirm the proof survived cleanup. A map that was never run is a draft.

## Refresh: keep the map honest

When a ticket changes a mapped feature, or a recipe fails for a reason that isn't a product bug:
- Fix the index: missing, dead or duplicate entries.
- Re-read the feature's source and update steps and expected results that drifted.
- Re-drive every changed recipe live before committing it.
- If the app is broken, report a bug; don't edit the map to match it.
- A refresh edits only `verify/`, never product code.
