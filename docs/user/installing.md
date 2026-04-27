# Installing per agent

The `rseng-agent-skills` CLI writes the pack into each agent's native location.
This page lists what lands where for every supported agent, how project and
user scope differ, and how to install inside a devcontainer or CI job.

## The CLI at a glance

```
npx rseng-agent-skills <command> [agents...] [--dry-run] [--pack-root <dir>]
```

Commands:

- `install [agents...]` - install the pack. With no agent named, it installs
  only for the agents it detects. Naming one or more agents forces those,
  detected or not.
- `update [agents...]` - refresh the managed files of an existing install,
  preserving any edits you made. It only acts on agents that already have an
  install (a manifest); if none exist it tells you to run `install` first.
- `doctor` - report per-agent install state: version, whether it is stale
  against the current pack, which managed files are intact, which you have
  edited, and which are missing.

Global options:

- `--dry-run` - report the planned changes and write nothing. Use it before
  any install to see the exact files.
- `--pack-root <dir>` - point at a different pack content root. This is for
  development against a local checkout; you do not need it for normal use.

Detection is based on directory markers. The CLI treats an agent as "in use"
when its marker directory exists (for example `.claude` in the project, or
`~/.codex` in your home directory). So `npx rseng-agent-skills install` on a repo
that already has `.github/` will install the Copilot files and nothing else.
To install for an agent you have not set up yet, name it explicitly:

```
npx rseng-agent-skills install gemini
```

## Project versus user scope

Some agents are installed into the current repository (project scope) and
some into your home directory (user scope):

| Agent | Scope | Marker | Installs into |
|---|---|---|---|
| Claude Code | project | `.claude/` | `.claude/skills/` |
| Claude Code | user | `~/.claude/` | `~/.claude/skills/` |
| Copilot | project | `.github/` | `.github/` |
| Cursor | project | `.cursor/` | `.cursor/rules/` |
| Codex CLI | user | `~/.codex/` | `~/.codex/` |
| Gemini CLI | user | `~/.gemini/` | `~/.gemini/extensions/rseng-agent-skills/` |

Project-scoped installs live with the repository, so they are shared with
anyone who clones it (and can be committed). User-scoped installs apply to
every project you open with that agent on your machine.

Claude Code has both a project and a user target. When you run
`install claude`, both are forced, so the skills land in `.claude/skills/`
and `~/.claude/skills/`. With a bare `install` (no agent named), only the
scopes whose marker directory exists are written.

## Claude Code

### Plugin route (recommended)

Claude Code has first-class plugin support, and this is the route that also
gives you the slash commands and the auditor subagent:

```
/plugin marketplace add fdiblen/rseng-agent-skills
/plugin install rseng-agent-skills
```

You get the 23 skills, the `/rseng-check`, `/rseng-cite` and
`/rseng-plan` commands, and the `rseng-auditor` subagent.

### File route

If you would rather have plain skill files - for example to commit them into
a repository, or to run Claude Code without the plugin system - install them
with the CLI:

```
npx rseng-agent-skills install claude
```

This copies the `skills/` folders into `.claude/skills/` (project) and
`~/.claude/skills/` (user). The file route installs the skills only; the
slash commands and auditor subagent come with the plugin.

## GitHub Copilot

```
npx rseng-agent-skills install copilot
```

Copilot is project-scoped. The install writes the pack's `.github` layout
into your repository's `.github/` directory: repository instructions,
per-skill instruction files, and the skill folders, all in the form Copilot
reads. Commit the `.github/` files to share the guidance with collaborators
and the Copilot coding agent.

## Cursor

```
npx rseng-agent-skills install cursor
```

Cursor is project-scoped. The install writes rule files into
`.cursor/rules/`: an always-on overview plus one rule per topic, in Cursor's
rules format.

## Codex CLI

```
npx rseng-agent-skills install codex
```

Codex is user-scoped. The install writes two things into `~/.codex/`:

- `AGENTS.md` - the top-level guidance Codex reads.
- `skills/` - the standard `SKILL.md` folders.

Because these are standard `AGENTS.md` plus `SKILL.md` layouts, the same
files work for other agents that follow those conventions (Zed, opencode,
Goose and similar).

## Gemini CLI

```
npx rseng-agent-skills install gemini
```

Gemini is user-scoped. The install writes a Gemini extension into
`~/.gemini/extensions/rseng-agent-skills/`, bundling the context, commands and
skills so Gemini loads them as one extension.

## Devcontainers

The repository ships a devcontainer feature at `features/rseng-agent-skills`. Add
it to your `devcontainer.json` to provision the pack when the container is
built. It takes a single `agents` option, a space-separated list, defaulting
to `claude`:

```json
{
  "features": {
    "./features/rseng-agent-skills": {
      "agents": "claude codex"
    }
  }
}
```

The feature is a thin bootstrap: it runs `npx rseng-agent-skills install` for the
agents you list, and installs after the Node feature so `npx` is available.

## Continuous integration

To provision the pack in a CI-driven agent job, run the install step before
the agent runs. The repository keeps a ready-made snippet at
`docs/snippets/github-action.yml`:

```yaml
# Provision the rseng-agent-skills pack for CI-driven coding agents.
# Add this step before any agent step that should follow RSQKit guidance
# (for example Claude Code GitHub Actions or Copilot coding agent jobs).
- name: Install rseng-agent-skills
  run: npx -y rseng-agent-skills install claude codex
```

Adjust the agent list to match the agent running in your workflow.
