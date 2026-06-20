# Quickstart

rseng-agent-skills packages research software engineering practice as native
files for AI coding agents. Pick your agent below for the fastest path to a
working install.

## What you get

One canonical pack, built into each agent's native format:

- 66 skills covering testing, CI/CD, documentation, licensing, citation
  metadata, FAIR software, publishing and releasing, reproducible
  environments, code quality, version control and review, maintenance and
  sustainability, management and planning, workflows, and an overall quality
  framework.
- For Claude Code only: twelve slash commands and six subagents on top
  of the skills.

Every skill teaches while it works; source-fed skills link back to the page their content came
from, so the guidance is traceable rather than generic.

## Claude Code

Claude Code installs as a plugin. Add the marketplace, then install the
plugin:

```
/plugin marketplace add fdiblen/rseng-agent-skills
/plugin install rseng-agent-skills
```

That gives you the full set:

- 66 skills the agent invokes when a task matches (for example, writing a
  CITATION.cff or setting up CI).
- Twelve slash commands:
    - `/rseng-check` - assess this repository against research software
      engineering practice.
    - `/rseng-cite` - generate or update `CITATION.cff` and
      `codemeta.json`.
    - `/rseng-plan` - draft a Software Management Plan skeleton.
    - `/rseng-release` - run the pre-release checklist and prepare a release.
    - `/rseng-reproduce` - clean-room reproduction check of the repository.
    - `/rseng-deps` - audit every dependency on all six vetting axes.
    - `/rseng-integrity` - pre-submission integrity battery for manuscript
      and results.
    - `/rseng-declare` - create or update the `aidecl.yaml` AI usage
      declaration.
    - `/rseng-metrics` - code and community health metrics snapshot.
    - `/rseng-digest` - draft the high-level project log digest for a period.
    - `/rseng-lesson` - record a lesson learned and draft its prevention
      artifact.
    - `/rseng-onboard` - generate a project-specific onboarding checklist.
- Six subagents:
    - `rseng-auditor` - read-only quality audit with severity-rated findings.
    - `rseng-reviewer` - code review that implements agreed improvements.
    - `rseng-librarian` - read-only citation and claim verification.
    - `rseng-scout` - read-only reuse and dependency scouting before you
      build or adopt.
    - `rseng-compliance-officer` - read-only regulatory and license
      compliance sweep.
    - `rseng-mentor` - teaching-focused walkthroughs on your real project.

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

Source-fed content derives from pinned community sources (credits in ATTRIBUTION.md and each skill's references.md); it
is adapted under CC-BY-4.0 and not endorsed by the upstream projects.
