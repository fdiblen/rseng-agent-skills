# rseng-agent-skills

Research software engineering (RSEng) skills for AI coding agents:
15 skills covering the practices that make research software good -
testing, CI/CD, documentation, licensing, citation, FAIR, publishing,
reproducibility, code review, code quality, maintenance, planning and
workflows - built into native formats for the major agents.

Skills teach while doing (verified "Learn more" links) and credit their
content sources whenever those shape an answer.

Reference content comes from pluggable content sources under
extensions/. The bundled source is [RSQKit](https://everse.software/RSQKit/)
(the Research Software Quality Kit by the EVERSE project), whose CC-BY-4.0
material feeds the skills' reference folders and checklists. This project
is independent and not endorsed by the EVERSE project. See
ATTRIBUTION.md.

## Agent support

| Agent | What you get | Install |
|---|---|---|
| Claude Code | 15 skills, /rseng-check, /rseng-cite, /rseng-plan, rseng-auditor agent | `/plugin marketplace add <owner>/rseng-agent-skills` then `/plugin install rseng-agent-skills` |
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
  topic, with generated references/ (source page fragments, tool lists,
  verified learn-more links, quality indicator checklists)
- commands/, agents/ - Claude Code slash commands and the auditor subagent
- pipeline/ - the source-agnostic build engine that ingests pinned
  content sources and regenerates everything above
- extensions/ - content sources; extensions/rsqkit/ is the bundled one
  (upstream pin, taxonomy, curated data)
- installer/ - the TypeScript CLI published to npm as `rseng-agent-skills`

## Versioning

Semantic versioning against the pack content: patch = regenerated content
only, minor = skill body updates or new skills, major = taxonomy
restructuring. Release notes state the pinned commit of every content
source a release was built from.

## Attribution

Guidance based on RSQKit by the EVERSE project and the RSQKit team,
https://everse.software/RSQKit/, DOI
[10.5281/zenodo.14923573](https://doi.org/10.5281/zenodo.14923573)
(CC-BY-4.0). Code is MIT licensed; adapted content remains CC-BY-4.0
(see LICENSE and LICENSE-content).
