# Changelog

Notable changes to the rseng-agent-skills pack. The format follows
keepachangelog.com; versions follow the semver policy in
docs/dev/release.md (patch = regeneration only, minor = skill body
changes or new skills, major = restructuring).

## [Unreleased]

## [0.1.0] - 2026-09-06

First public release.

### Added

- 67 skills covering research software engineering practice: core
  engineering, reproducibility and workflows, research data, numerics
  and performance, publishing and credit, integrity, security and
  compliance, communication and interfaces, community and people, and
  specialized areas (ML, GPU, HPC, big data, notebooks).
- 14 workflow commands and 6 subagents for Claude Code, including the
  rseng-panel multi-perspective review.
- A phased practice-enforcement layer (7 hooks): session context
  injection, phase status, a write gate requiring a ledger-backed
  coverage worklog, consultation nudges, relevance signals with
  privacy warnings, and a Stop-time quality audit.
- One canonical .agents/skills tree consumed by the Claude Code, GitHub
  Copilot, Cursor, Codex CLI, Gemini CLI and Google Antigravity targets;
  per-agent install via the npm installer. An install resolves to project
  scope when the agent's marker directory exists and user scope
  otherwise, and prints the directory it wrote to.
- Pipeline quality gates in CI: token budgets, frontmatter lint,
  reference link checks, hook behaviour tests, REUSE compliance, and a
  zero-drift check that regenerates every derived file and fails if a
  committed one differs.
- Install and update protect what is already there: a file holding
  something other than what the pack put there is copied into an
  .rseng-backup-* directory before being written, update preserves files
  you have edited, and update removes files a release no longer ships
  only when their content is untouched and no other installed agent
  still claims them.
- Both licence texts, ATTRIBUTION.md and NOTICE travel with the content
  into every bundle and every install destination.
- Citation and archive metadata: CITATION.cff, codemeta.json,
  ATTRIBUTION.md and NOTICE crediting the RSQKit (EVERSE) and
  Netherlands eScience Center guide heritage.

[Unreleased]: https://github.com/fdiblen/rseng-agent-skills/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/fdiblen/rseng-agent-skills/releases/tag/v0.1.0
