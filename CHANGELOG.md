# Changelog

Notable changes to the rseng-agent-skills pack. The format follows
keepachangelog.com; versions follow the semver policy in
docs/dev/release.md (patch = regeneration only, minor = skill body
changes or new skills, major = restructuring).

## [Unreleased]

## [0.1.0] - 2026-08-29

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
- One canonical .agents/skills tree consumed by Claude Code, GitHub
  Copilot, Cursor, Codex CLI and Gemini CLI targets; per-agent
  install via the npm installer (project-scope, nothing written to
  user configuration).
- Pipeline quality gates in CI: token budgets, frontmatter lint,
  deterministic routing evals, reference link checks, offline hook
  tests, and an agent-in-the-loop test harness with token/context
  analytics (markdown and self-contained HTML reports).
- Citation and archive metadata: CITATION.cff, codemeta.json,
  ATTRIBUTION.md and NOTICE crediting the RSQKit (EVERSE) and
  Netherlands eScience Center guide heritage.

[Unreleased]: https://github.com/fdiblen/rseng-agent-skills/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/fdiblen/rseng-agent-skills/releases/tag/v0.1.0
