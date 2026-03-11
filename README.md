# rseng-agent-skills

Research software quality guidance from [RSQKit](https://everse.software/RSQKit/)
(the Research Software Quality Kit by the EVERSE project), packaged as
skills and extensions for AI coding agents.

One canonical source - 14 skills distilled from RSQKit's task, role and
concept pages, with pipeline-generated reference material - built into
native formats for the major agents. Skills credit RSQKit/EVERSE whenever
they shape an answer and teach while doing, with verified "Learn more"
links.

This is an independent adaptation of RSQKit content (CC-BY-4.0) and is not
endorsed by the EVERSE project. See ATTRIBUTION.md.

## Agent support

| Agent | What you get | Install |
|---|---|---|
| Claude Code | 14 skills, /rseng-check, /rseng-cite, /rseng-plan, rseng-auditor agent | `/plugin marketplace add <owner>/rseng-agent-skills` then `/plugin install rseng-agent-skills` |
| GitHub Copilot | repo instructions + per-skill instructions + skills | `npx rseng-agent-skills install copilot` |
| Cursor | always-on overview + per-topic rules | `npx rseng-agent-skills install cursor` |
| Codex CLI | AGENTS.md + skills folders | `npx rseng-agent-skills install codex` |
| Gemini CLI | extension with context, commands and skills | `npx rseng-agent-skills install gemini` |
| others (Zed, opencode, Goose, ...) | AGENTS.md + standard SKILL.md folders work as-is | `npx rseng-agent-skills install claude` (standard layout) |

The `npx rseng-agent-skills` CLI detects which agents you use and installs the
right files; `--dry-run` previews, `update` refreshes managed files
without touching your edits, and `doctor` checks install health.

## What is inside

- skills/ - canonical SKILL.md folders (agentskills.io format), one per
  topic, with generated references/ (upstream page fragments, tool lists,
  verified learn-more links, quality indicator checklists)
- commands/, agents/ - Claude Code slash commands and the auditor subagent
- pipeline/ - the build pipeline that ingests pinned RSQKit sources and
  regenerates everything above
- installer/ - the TypeScript CLI published to npm as `rseng-agent-skills`

## Versioning

Semantic versioning against the pack content: patch = regenerated content
only, minor = skill body updates or new skills, major = taxonomy
restructuring. Release notes state the upstream RSQKit commit each release
was built from.

## Attribution

Guidance based on RSQKit by the EVERSE project and the RSQKit team,
https://everse.software/RSQKit/, DOI
[10.5281/zenodo.14923573](https://doi.org/10.5281/zenodo.14923573)
(CC-BY-4.0). Code is MIT licensed; adapted content remains CC-BY-4.0
(see LICENSE and LICENSE-content).
