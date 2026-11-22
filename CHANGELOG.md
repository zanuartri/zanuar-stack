# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow [Semantic Versioning](https://semver.org/).

## [0.8.0]

### Added
- Choose direct, light or full orchestration and keep the existing work when moving from light to full.

### Changed
- Use `craft` in place of `root-cause`, `cut-first`, `test-first` and `comment-sweep`.
- Use `plan` in place of `big-plan`, `shape-first` and `brief`.
- Find `ripple-check` in `reviewer` and `pr-comments` in `watch-pr`.

## [0.7.0]

### Added
- Review recurring delivery failures with `retro` using ticket history or merged PR reviews in lite mode.
- Add ticket database queries for fix rounds by initial worker model and failed runs by harness.

## [0.6.2]

### Changed
- Restructure the README for open-source readers; add CHANGELOG and CONTRIBUTING.

## [0.6.1]

### Changed
- One owner voice: with an orchestrator running, managers go through it; managers interview the owner only when started directly.
- Install docs: pick one route per agent (plugin or skills.sh, not both).

## [0.6.0]

### Added
- Bootstrap new repos from the orchestrator.
- Lite mode: run a team without a ticket database.

## [0.5.1]

### Fixed
- Enforce reviewed ticket delivery across harnesses.

## [0.5.0]

### Added
- Connect design and engineering agent teams (`design-handoff`).

## [0.4.3]

### Added
- Repo defaults for ticket dispatch and integration branch.

## [0.4.2]

### Added
- Per-ticket worker and reviewer overrides.

## [0.4.1]

### Fixed
- Pilot friction in setup; verify setup on Linux, macOS and Windows.

## [0.4.0]

### Added
- Per-repo autonomy (`ask`/`review`/`merge`) and landing policy.
- Local PR watcher.

## [0.3.0]

### Added
- `comment-sweep` and `make-verify` skills, adapted from pstack.

## [0.2.0]

### Added
- Claude Code and Codex plugin manifests, skills.sh install, and the `setup-zanuar-stack` skill.

## [0.1.0]

### Added
- Initial skills: orchestrator (first named "lead"), manager, worker, reviewer and the practice skills.
- Orca adapter.
