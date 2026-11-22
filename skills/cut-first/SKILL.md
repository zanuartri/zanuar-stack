---
name: cut-first
description: Before adding, refactoring or rewriting, remove what is dead or redundant first, then build on the smaller base. Use when planning an addition or refactor, or when the owner says cut first, simplify, or "subtract before you add".
---

# Cut first

Default to subtraction. Leave the system a little simpler than you found it, with the same or a smaller surface.

- **Remove before you build**: dead code, unused flags, redundant validators, stub references. Land the removal first, then the addition.
- **Get to the minimum before polishing.**
- **Design for what is actually used**, not for imagined edge cases.
- **No speculative guards, parsers or validators** beyond what the spec needs.
- **Prompts and docs too**: drop repeated instructions and oversized templates.
- **A reference with nothing new in it gets deleted**, not left as a stub.

In a ticket, put the cut as its own acceptance line ("`oldHelper` removed, no callers left") so the reviewer checks it.
