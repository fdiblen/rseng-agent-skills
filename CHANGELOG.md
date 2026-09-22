# Changelog

Notable changes to the rseng-agent-skills pack. The format follows
keepachangelog.com; versions follow the semver policy in
docs/dev/release.md (patch = regeneration only, minor = skill body
changes or new skills, major = restructuring).

## [Unreleased]

## [0.2.0] - 2026-09-23

### Fixed

- The consultation ledger now understands the namespaced skill names a
  plugin host reports (`<plugin>:<skill>`). They were matched whole against
  the bare inventory and discarded, so on a plugin install the ledger stayed
  empty however many skills a session opened and the write gate held every
  write until the checks were switched off by hand.
- Environment declarations are recognised for every language the code scan
  accepts, not only Python: `package.json`, `DESCRIPTION`, `renv.lock`,
  `Project.toml`, `CMakeLists.txt`, `meson.build`, `conanfile.txt` and
  `vcpkg.json`. A JavaScript project was told it had no dependency
  declaration and had no way to satisfy the demand.
- Coverage output and bytecode are no longer read as the project's own work,
  so a vendored `cacert.pem` under a virtualenv and files under `htmlcov/`
  stop raising security and interface findings.
- The gate no longer holds writes outside the project, and a filename quoted
  inside a heredoc is no longer treated as a file being written.
- The stop-time message says the pass runs once, instead of implying the
  session is stuck.

### Changed

- The published package now contains only files git tracks, plus the
  generated adapters. Packing refuses to run where it cannot ask git.
- The self-check shipped to the hookless agents accepts the same environment
  declarations as the hooks, and a test keeps the two lists in step.

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
