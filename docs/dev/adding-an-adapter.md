# Adding an adapter

An adapter (called a "target" in the pipeline) turns the canonical skills into
the guidance layout one specific agent expects. Targets are small: each is a
module under `pipeline/src/rseng_pipeline/targets/` that registers a build
function, plus a folder of Jinja templates under `adapters/templates/<name>/`.
The build framework in `adapters.py` supplies the render context and the
template environment; the target decides what files to emit and where.

There are four building blocks every target uses from `..adapters`:

- `render_to(env, template_name, context, out)` - render one template to one
  output path.
- `copy_skills(repo_root, target_dir)` - passthrough: copy the canonical
  skill folders (SKILL.md plus the generated `references.md`)
  verbatim into the target.
- `build_agents_skills(repo_root, context, target_dir)` - the unified
  native tree: `.agents/skills/` holding every canonical skill plus one
  generated command-skill per plugin command. Command-skills are
  explicitly invoked: their frontmatter carries
  `disable-model-invocation: true` and each ships an
  `agents/openai.yaml` disabling implicit invocation for Codex
  (`rseng-panel` is excluded as Claude-only).
- `copy_check(repo_root, target_dir)` - ship the platform-neutral
  self-check (`rseng-check/rseng_check.py` plus the hooks' JSON data files)
  next to the target's context files; hookless agents are instructed to
  run it before finishing.

A target combines these however its agent needs. The three unified
targets (Copilot, Cursor, Codex) follow one shape - a single thin
rendered context file carrying the behavior rules, the unified
`.agents/skills/` tree the agent reads natively, and the self-check
folder. The `gemini` target follows the same shape; the TOML command
format it used to ship is retired, and command-skills in the unified
tree replace it.

`gemini-extension` is the exception, and it is worth reading before you
assume a new target can reuse `build_agents_skills` as-is. Gemini CLI
loads extensions from `~/.gemini/extensions/<name>/` and requires
`gemini-extension.json` in the root, reads their skills from `skills/`
rather than `.agents/skills/`, and takes their hooks from
`hooks/hooks.json` with `${extensionPath}`-relative commands. A bundle
missing any of that installs without error and is then never loaded.

Every target needs an entry in `_structure_problems`; a target with no
entry is rejected rather than passing an empty check.

## The render context

`load_render_context(repo_root)` in `adapters.py` builds one dict shared by
every template. Its keys:

- `generated_note` - the "do not edit" banner string.
- `skills` - a list of `{name, description, scope, brief, related}` per
  skill: the description from the skill's `SKILL.md` frontmatter, the
  scope and brief derived from its coverage half, and the related skills
  (with reasons) from `hooks/related.json`.
- `commands` - a list of `{name, description, body}` read from the plugin's
  `commands/*.md` files.

The Jinja environment (`template_env`) uses `StrictUndefined`, so a template
that references a key not in the context fails loudly at build time rather than
rendering a blank.

## 1. Write the target module

Create `pipeline/src/rseng_pipeline/targets/<name>.py`. Register the build
function with the `@target("<name>")` decorator and return the list of files
written. The two real patterns to copy from:

Body translation - when a target reuses the Claude command bodies but needs
the Claude-specific placeholders rewritten. The unified targets render each
command as a skill in `.agents/skills/`, rewriting the placeholders on the
way (`adapters.py`):

```python
body = command["body"].replace("${CLAUDE_PLUGIN_ROOT}/", ".agents/")
body = body.replace("$ARGUMENTS", "any arguments provided with the invocation")
```

The placeholder rewrite is not optional: `${CLAUDE_PLUGIN_ROOT}` and
`$ARGUMENTS` are Claude-only, and the post-render checks fail the build if
`CLAUDE_PLUGIN_ROOT` reaches a non-Claude output (see checks below). Whenever a
target reuses command bodies, translate them. Gemini's per-command
render passes an extended context (`{**context, "command": adapted}`)
so the template can reference `command` directly.

Thin context plus the unified tree (Copilot) - render the repo-wide
instructions, then emit the shared native tree and the self-check:

```python
@target("copilot")
def build_copilot(repo_root, env, context, target_dir):
    github_dir = target_dir / ".github"
    written = [render_to(env, "copilot/copilot-instructions.md.j2",
                         context, github_dir / "copilot-instructions.md")]
    written += build_agents_skills(repo_root, context, target_dir)
    written += copy_check(repo_root, github_dir)
    return written
```

`cursor.py` is the same shape with a single always-on
`.cursor/rules/rseng-overview.mdc` rule as its context file. `codex.py`
shows a third wrinkle: it size-checks its generated `AGENTS.md`
against the budget in `SIZE_BUDGETS` inside the build function and
raises if it is exceeded, because Codex loads the file whole on every
session.

## 2. Add the templates

Put the target's Jinja templates under `adapters/templates/<name>/`. The
environment has `trim_blocks` and `lstrip_blocks` on and keeps trailing
newlines. Templates read from the render context; a per-skill or per-command
template also sees the injected `skill` or `command` key. Match the output
format the agent expects (frontmatter for Cursor rules and for rendered
command-skills, plain Markdown for context files), and emit
the `generated_note` banner near the top so the output is visibly generated.
The existing folders under `adapters/templates/` are the reference for each
format.

## 3. Register the target

Import the new module in `pipeline/src/rseng_pipeline/targets/__init__.py` so
the decorator runs and populates `TARGETS`:

```python
from . import codex, copilot, cursor, gemini  # noqa: F401
```

Add your module to that import line. Importing the package is what registers
every target; `build_adapters` iterates `sorted(TARGETS)` when no explicit
target list is given.

## 4. Output checks

`checks.py` runs `check_target(dist/<name>)` after each target renders, and any
problem it returns fails the whole build. It is format-driven, so a new target
is covered automatically as long as its filenames match the conventions:

- **Size budgets** - files agents load whole have a byte budget
  (`copilot-instructions.md` 16 KiB, `GEMINI.md` 24 KiB, `AGENTS.md` 32 KiB).
  If your target emits a whole-file context doc, add its filename and budget to
  `SIZE_BUDGETS`.
- **Frontmatter fields** - `*.instructions.md` must carry `description` and
  `applyTo`; `*.mdc` must carry `description` and `alwaysApply`. Extend
  `_FRONTMATTER_REQUIRED` if your target introduces a new required-frontmatter
  file suffix.
- **JSON validity** - rendered JSON must parse and carry `description`
  and `prompt`; `.json` files must parse.
- **Leak detection** - any output containing `CLAUDE_PLUGIN_ROOT` fails, and
  `.md`/`.mdc` files containing `{%` are flagged as unrendered template
  residue (SKILL.md and references.md passthrough files are exempt,
  since they are validated at their canonical source).

If your target needs a check the current rules do not express, add it to
`_check_file`.

## 5. The installer side

The installer (`installer/`) copies the built pack into whatever agent
directories it detects. Two files must learn about a new agent.

`installer/src/install.ts` - add an entry to the `SOURCES` whitelist keyed by
agent name. It lists what to copy from the built pack and where, relative to
the target's install directory. Sources are an explicit whitelist on purpose,
so an install never sweeps up stray files:

```typescript
const SOURCES: Record<string, { from: string; to: string }[]> = {
  claude: [
    { from: "skills", to: "skills" },
    { from: "commands", to: "commands" },
    { from: "agents", to: "agents" },
  ],
  copilot: [
    { from: "dist/copilot/.github", to: ".github" },
    { from: "dist/copilot/.agents", to: ".agents" },
  ],
  cursor: [
    { from: "dist/cursor/.cursor", to: ".cursor" },
    { from: "dist/cursor/.agents", to: ".agents" },
  ],
  codex: [
    { from: "dist/codex/AGENTS.md", to: "AGENTS.md" },
    { from: "dist/codex/.agents", to: ".agents" },
    { from: "dist/codex/rseng-check", to: "rseng-check" },
  ],
  gemini: [{ from: "dist/gemini", to: "." }],
};
```

Point `from` at your `dist/<name>/` output. A missing source path throws
`missing pack content ... (run the adapter build first)`, so the whitelist
entry and the build output must agree.

`installer/src/agents.ts` - add an `AgentSpec` to `SPECS`. It declares the
agent name, its scope (`project` drops files into the current repo, `user`
into the home directory), a `marker` directory whose presence means the agent
is in use (used for auto-detection), and the `installDir` where the pack lands.
The unified targets (copilot, cursor, codex) are project-scoped with the
project root as their install directory, so their shared `.agents/skills/`
tree lands once per repository (codex is detected by `~/.codex` in the
home directory but still installs into the project). Gemini is
user-scoped, marked by `~/.gemini`, and installs into
`~/.gemini/extensions/rseng-agent-skills`. Because several agents can share one
install directory, each install records its files in a per-agent
manifest, `.rseng-agent-skills.<agent>.json`. Match the layout your `SOURCES`
entry copies into.

## 6. Validate

- Build just your target: `uv run --directory pipeline python -m rseng_pipeline.build_adapters <name>`
  and confirm `dist/<name>/` looks right and the checks passed.
- Build the installer and run its tests: `cd installer && npm run build && npm test`.
- Try a dry-run install to confirm detection and the copy plan
  (`executePlan` logs the planned files under `[dry-run]`).
