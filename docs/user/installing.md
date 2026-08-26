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
| Google Antigravity | project | `.agents/` | project root: `GEMINI.md` + `AGENTS.md` + `.agents/skills/` + `rseng-check/` |
| Google Antigravity | user | `~/.gemini/` | `~/.gemini/config/` (global skills and rules) |
| Gemini CLI | project | `GEMINI.md` | project root: `GEMINI.md` + `.agents/skills/` + `rseng-check/` |
| Gemini CLI | user | `~/.gemini/` | `~/.gemini/extensions/rseng-agent-skills/` |
| Copilot | project | `.github/` | project root: `.github/` + `.agents/skills/` |
| Cursor | project | `.cursor/` | project root: `.cursor/` + `.agents/skills/` |
| Codex CLI | project | `~/.codex/` | project root: `AGENTS.md` + `.agents/skills/` + `rseng-check/` |

Project-scoped installs live with the repository, so they are shared with
anyone who clones it (and can be committed). User-scoped installs apply to
every project you open with that agent on your machine.

Google Antigravity, Copilot, Cursor, Codex, and Gemini CLI all read the same native
skills tree, `.agents/skills/`, so installing for more than one of them shares that
tree at the project root. Each install records its own files in a
per-agent manifest (`.rseng-agent-skills.<agent>.json`), so `update` and
`doctor` track every agent separately even in the same directory.

Claude Code has both a project and a user target. When you run
`install claude`, both are forced, so the skills land in `.claude/skills/`
and `~/.claude/skills/`. With a bare `install` (no agent named), only the
scopes whose marker directory exists are written.

## Google Antigravity

```bash
# Project-scoped install (recommended for teams and repos):
npx rseng-agent-skills install antigravity --scope project

# User-scoped install (applies across all local workspaces):
npx rseng-agent-skills install antigravity --scope user
```

Antigravity (the IDE and the `agy` CLI) reads from several places. A
project-scoped install writes the behaviour rules to `GEMINI.md` and
`AGENTS.md`, the skills to `.agents/skills/`, project-wide rules to
`.agents/rules/`, and the self-check to `rseng-check/`. Skill bodies are not
loaded up front - the tree carries names and scopes, and a skill is opened
when it becomes relevant. A user-scoped install puts the skills in
`~/.gemini/config/skills/` instead, where they apply to every project on the
machine. Slash commands, tools and subagents run natively.

## Gemini CLI

```bash
# User-scoped extension:
npx rseng-agent-skills install gemini --scope user

# Or project-scoped workspace tree:
npx rseng-agent-skills install gemini --scope project
```

For Gemini CLI the installer either provisions
`~/.gemini/extensions/rseng-agent-skills/` as a bundled extension carrying the
context file, the skill descriptions and the command workflows, or drops
`.agents/skills/` and `GEMINI.md` straight into the current repository.

## Claude Code

### Plugin route (recommended)

Claude Code has first-class plugin support, and this is the route that also
gives you the slash commands and the subagents:

```
/plugin marketplace add fdiblen/rseng-agent-skills
/plugin install rseng-agent-skills
```

You get the 67 skills, the fourteen `/rseng-*` commands and the six
subagents (`rseng-auditor`, `rseng-reviewer`, `rseng-librarian`, `rseng-scout`,
`rseng-compliance-officer`, `rseng-mentor`). See
[Using the skills](using.md) for what each command and subagent does.

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

Copilot is project-scoped. The install writes the repository
instructions into `.github/` (with the self-check under
`.github/rseng-check/`) and the skill folders into `.agents/skills/`,
which Copilot reads natively across its whole surface - agent mode,
the CLI, code review and the cloud coding agent. Commit the files to
share the guidance with collaborators.

## Cursor

```
npx rseng-agent-skills install cursor
```

Cursor is project-scoped. The install writes a single always-on
overview rule into `.cursor/rules/` (with the self-check under
`.cursor/rseng-check/`) and the skill folders into `.agents/skills/`,
which Cursor loads natively by description relevance. The command
workflows are in the same tree as explicitly-invoked skills
(`/rseng-check` and friends).

## Codex CLI

```
npx rseng-agent-skills install codex
```

Codex is project-scoped (it is detected by `~/.codex/` in your home
directory, but the files land in the repository). The install writes
three things into the project root:

- `AGENTS.md` - compact top-level guidance: the behavior rules plus the
  full skill-name inventory. Codex's native startup skills listing has
  a context budget and may truncate the visible list; the inventory in
  `AGENTS.md` compensates.
- `.agents/skills/` - the standard `SKILL.md` folders, read natively by
  Codex, including the explicitly-invoked command-skills (`$rseng-check`
  and friends).
- `rseng-check/` - the dependency-free self-check.

Because these are standard `AGENTS.md` plus `.agents/skills/` layouts,
the same files work for other agents that follow those conventions
(Zed, opencode, Goose and similar).

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
That means it needs the package on npm - it will not work against an
unpublished checkout. Until the first release, install from a clone instead:
build the adapters and the CLI, then run `node installer/dist/cli.js install`
with `--pack-root` pointing at the checkout.

## Continuous integration

To provision the pack in a CI-driven agent job, run the install step before
the agent runs. The repository keeps a ready-made snippet at
`docs/snippets/github-action.yml`:

```yaml
# Provision the rseng-agent-skills pack for CI-driven coding agents.
# Add this step before any agent step that should follow the pack's guidance
# (for example Claude Code GitHub Actions or Copilot coding agent jobs).
- name: Install rseng-agent-skills
  run: npx -y rseng-agent-skills install claude codex
```

Adjust the agent list to match the agent running in your workflow.

## Permissions and trust

What each surface asks for, and why:

- Plugin or installer users: the pack ships NO pre-approved tool
  permissions. Where hooks are installed - the Claude plugin carries
  them, and `install codex` and `install gemini` write a hook config -
  the agent shows its standard one-time trust confirmation for that
  file on first launch. `install claude` copies skills, commands and
  subagents only, and adds no hooks. Nothing is approved on your
  behalf either way, and every tool call is prompted per your own
  permission settings.
- Contributors working in a checkout of this repository: the same -
  the repository does not commit or ship a `settings.local.json`,
  so a fresh checkout pre-approves nothing. Approvals you grant
  during your own sessions accumulate locally and stay local.
- Test-harness sandboxes: headless runs use the agent CLI's own
  skip-permissions flag inside a throwaway sandbox; interactive
  sandboxes prompt per tool like any project.

If a trust dialog ever lists pre-approved permissions, they came
from your own local sessions, not from this pack; they are safe to
clear.
