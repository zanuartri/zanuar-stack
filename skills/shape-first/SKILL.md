---
name: shape-first
description: Sketch types, signatures and module boundaries before writing code, compare two shapes, and pick one. Use for non-trivial or hard-to-reverse design work, or when the owner says shape first, architect, or "design this before coding".
---

# Shape first

Code locks in a shape. Choose the shape on purpose.

1. **Trace** every system the change touches: callers, data, storage, wire formats.
2. **Sketch two genuinely different shapes**: types, function signatures, which module owns what. A few lines each, no bodies.
3. **Pick** the one where:
   - each piece of state has exactly one owner,
   - each task has one obvious way to do it,
   - callers need to know the least.
4. Write the chosen sketch into the ticket so the worker builds that shape, not a new one.
5. While it's being built, watch for repeated workarounds. Two in a row means the shape is wrong: redesign instead of patching.

For a large or disputed design, ask two different models (or a worker and the reviewer) for a shape each and compare before choosing.
