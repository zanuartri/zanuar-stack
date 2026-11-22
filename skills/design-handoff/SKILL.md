---
name: design-handoff
description: Hand a design to engineering in a format ready for an implementation brief, or request a design using the same headings.
---

# Design handoff

Design fills these headings when handing work to engineering. Engineering uses the same headings to request a design and marks open decisions for design to fill in.

## Goal and user

Name the user, what they need to do, and what success looks like.

## Screens and states

List the screens and link their designs. Cover empty, loading, error, and success states where they apply.

## Design tokens and assets

Name the tokens and assets to use. Give a repo path or shared link for each source.

## Interactions

Describe what happens after each key action, including recovery from errors.

## Responsive rules

Specify the widths or conditions that change the layout and what reflows, moves, or hides.

## Accessibility notes

Specify keyboard behavior, focus order, accessible names, and any contrast or reduced-motion requirements.

## Acceptance checks

Give each check a screen, state, viewport, and expected visible result a reviewer can verify from a screenshot. For behavior a screenshot cannot prove, give steps and the expected result.

## Out of scope

List the screens, states, or behavior this work leaves for later.

The orchestrator turns the handoff into a story and carries the relevant headings into each repo brief as written. Use the interview skill only for gaps that affect implementation or acceptance.
