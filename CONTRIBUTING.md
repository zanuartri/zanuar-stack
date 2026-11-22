# Contributing

## Propose a skill

Open an issue first: what problem it solves and why no existing skill covers it. A skill is a folder `skills/<name>/SKILL.md` with `name` and `description` frontmatter; the description says when to use it. Keep it short and concrete. Add it to the tables in the README, and credit any source in the Credits table.

## Check your change

```sh
scripts/check.sh
```

This is what the Portability CI runs (Linux, macOS, Windows). It must pass.

## Versioning

Any change to `skills/` or other shipped content bumps `version` in `.claude-plugin/plugin.json` (users only get updates when it changes): patch for fixes and docs, minor for new behavior or skills. Add an entry to `CHANGELOG.md`.

## Pull requests

Branch from `main`, open a PR, keep it small. Never push to `main` directly.
