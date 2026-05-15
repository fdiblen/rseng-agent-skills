# Quickstart

rseng-agent-skills packages RSQKit research software quality guidance as native
files for AI coding agents. Pick your agent below for the fastest path to a
working install.

## What you get

One canonical pack, built into each agent's native format:

- 51 skills covering testing, CI/CD, documentation, licensing, citation
  metadata, FAIR software, publishing and releasing, reproducible
  environments, code quality, version control and review, maintenance and
  sustainability, management and planning, workflows, and an overall quality
  framework.
- For Claude Code only: three slash commands and an auditor subagent on top
  of the skills.

Every skill teaches while it works and links back to the RSQKit page it came
from, so the guidance is traceable rather than generic.

## Claude Code

Claude Code installs as a plugin. Add the marketplace, then install the
plugin:

```
/plugin marketplace add fdiblen/rseng-agent-skills
/plugin install rseng-agent-skills
```

That gives you the full set:

- 51 skills the agent invokes when a task matches (for example, writing a
  CITATION.cff or setting up CI).
- Three slash commands:
    - `/rseng-check` - assess this repository against the RSQKit quality
      indicator checklists.
    - `/rseng-cite` - generate or update `CITATION.cff` and
      `codemeta.json`.
    - `/rseng-plan` - draft a Software Management Plan skeleton.
- The `rseng-auditor` subagent, a read-only quality auditor you can invoke
  for a health check before a release or publication.

If you prefer plain skill files over the plugin (or you run Claude Code
without the plugin system), the CLI can drop the same skills into
`.claude/skills/` instead - see [Installing per agent](installing.md).

## Every other agent

Copilot, Cursor, Codex CLI, Gemini CLI and any agent that reads `AGENTS.md`
plus standard `SKILL.md` folders install through the CLI:

```
npx rseng-agent-skills install <agent>
```

Replace `<agent>` with `copilot`, `cursor`, `codex`, `gemini`, or `claude`
(the standard-layout skill files). Run with no agent named to install only
for the agents the CLI detects in your project and home directory:

```
npx rseng-agent-skills install
```

Before writing anything, preview with `--dry-run`:

```
npx rseng-agent-skills install cursor --dry-run
```

This reports the files that would be written and touches nothing. Two more
commands round out the CLI: `npx rseng-agent-skills update` refreshes the managed
files of an existing install without overwriting your edits, and
`npx rseng-agent-skills doctor` reports install health per agent. See
[Installing per agent](installing.md) for the exact paths each agent uses,
project-versus-user scope, the devcontainer feature and a CI snippet.

---

Content derives from [RSQKit](https://everse.software/RSQKit/) by the EVERSE
project (CC-BY-4.0); see the attribution notes for details.
