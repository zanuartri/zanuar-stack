---
name: ripple-check
description: Find what a change could break outside its own diff, and prove the one fact that makes it safe by running real code. Use for risky or shared changes, a small diff you don't trust, or when the owner asks "what could this break" or for the blast radius.
---

# Ripple check

Listing callers is the easy part; grep does it. The job is the breakage grep can't see.

## Steps
1. **Read the change**: what it adds, changes and deletes, including behaviour the diff doesn't spell out.
2. **Find the one fact it's safe because of** (e.g. "this only drops cache entries that are already dead"). Most risky-looking changes hinge on one such fact. Spend your time here.
3. **Look past grep**: library source at the pinned version, timing (async, teardown, ordering), JSON shapes, DB columns, wire formats, other languages reading the same data, feature flags, code a few hops downstream.
4. **Rate each risk**: how likely, how bad, `file:line`. Never invent a caller or API; "searched, found none" is an answer.
5. **Prove the key fact** with a small script or test that calls the real code and fails loudly if you're wrong. Run it and paste the output.

## How sure is each claim
said so < pointed at the line < walked the failure and it can't happen < ran it < reproduced in the real app. Say where each one stopped.

## Hand back
- What it does (including the non-obvious part).
- The safety fact, its proof level, and the proof (or "unproven").
- Confirmed risks, then cleared ones and why.
- The cheapest test or repro to run before merging.
