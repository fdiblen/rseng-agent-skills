# Adding an adapter

An adapter (called a "target" in the pipeline) turns the canonical skills into
the guidance layout one specific agent expects. Targets are small: each is a
module under `pipeline/src/rseng_pipeline/targets/` that registers a build
function, plus a folder of Jinja templates under `adapters/templates/<name>/`.
The build framework in `adapters.py` supplies the render context and the
template environment; the target decides what files to emit and where.

There are three building blocks every target uses from `..adapters`:

- `render_to(env, template_name, context, out)` - render one template to one
  output path.
- `copy_skills(repo_root, target_dir)` - passthrough: copy the canonical
  skill folders (SKILL.md plus the generated `references.md`)
  verbatim into the target.
- `copy_check(repo_root, target_dir)` - ship the platform-neutral
  self-check (`rseng-check/rseng_check.py` plus the hooks' JSON data files)
  next to the target's context files; hookless agents are instructed to
  run it before finishing.

A target combines these however its agent needs. All four established
targets follow the same shape - a few rendered context/instruction
files, translated command files, the canonical skill folders copied in
whole so the agent can open the real SKILL.md and its references, and
the self-check folder.

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

Body translation (Gemini) - when the agent reuses the Claude command bodies
but needs the Claude-specific placeholders rewritten. `gemini.py` renders an
extension manifest, a `GEMINI.md` context file and one TOML file per command,
running each command body through a small translator first:

```python
def _gemini_body(body: str) -> str:
    translated = body.replace("${CLAUDE_PLUGIN_ROOT}/", "the extension's ")
    translated = translated.replace("$ARGUMENTS", "{{args}}")
    return translated
```

The placeholder rewrite is not optional: `${CLAUDE_PLUGIN_ROOT}` and
`$ARGUMENTS` are Claude-only, and the post-render checks fail the build if
`CLAUDE_PLUGIN_ROOT` reaches a non-Claude output (see checks below). Whenever a
target reuses command bodies, translate them.

Rendered plus passthrough (Copilot) - render a repo-wide summary, one
instruction file per skill and one prompt file per command, then copy
the skill folders and the self-check in whole:

```python
@target("copilot")
def build_copilot(repo_root, env, context, target_dir):
    github_dir = target_dir / ".github"
    written = [render_to(env, "copilot/copilot-instructions.md.j2",
                         context, github_dir / "copilot-instructions.md")]
    for skill in context["skills"]:
        written.append(render_to(
            env, "copilot/skill.instructions.md.j2",
            {**context, "skill": skill},
            github_dir / "instructions" / f"{skill['name']}.instructions.md"))
    for command in context["commands"]:
        adapted = {**command, "body": _copilot_body(command["body"])}
        written.append(render_to(
            env, "copilot/command.prompt.md.j2",
            {**context, "command": adapted},
            github_dir / "prompts" / f"{command['name']}.prompt.md"))
    copy_skills(repo_root, github_dir / "skills")
    written.extend(sorted((github_dir / "skills").rglob("SKILL.md")))
    written.extend(copy_check(repo_root, github_dir))
    return written
```

Note the per-item render passes an extended context (`{**context, "skill": skill}`)
so the template can reference `skill` directly. `codex.py` shows a third wrinkle:
it size-checks its generated `AGENTS.md` against a 32 KiB budget inside the
build function and raises if it is exceeded, because Codex only reads the first
32 KiB of a project doc.

## 2. Add the templates

Put the target's Jinja templates under `adapters/templates/<name>/`. The
environment has `trim_blocks` and `lstrip_blocks` on and keeps trailing
newlines. Templates read from the render context; a per-skill or per-command
template also sees the injected `skill` or `command` key. Match the output
format the agent expects (frontmatter for Copilot instructions and Cursor
rules, TOML for Gemini commands, plain Markdown for context files), and emit
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
- **TOML / JSON validity** - `.toml` files must parse and carry `description`
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
  copilot: [{ from: "dist/copilot/.github", to: "." }],
  cursor: [{ from: "dist/cursor/.cursor", to: "." }],
  codex: [
    { from: "dist/codex/AGENTS.md", to: "AGENTS.md" },
    { from: "dist/codex/skills", to: "skills" },
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
For example, Gemini is user-scoped, marked by `~/.gemini`, and installs into
`~/.gemini/extensions/rseng-agent-skills`. Match the layout your `SOURCES` entry
copies into.

## 6. Validate

- Build just your target: `uv run --directory pipeline python -m rseng_pipeline.build_adapters <name>`
  and confirm `dist/<name>/` looks right and the checks passed.
- Build the installer and run its tests: `cd installer && npm run build && npm test`.
- Try a dry-run install to confirm detection and the copy plan
  (`executePlan` logs the planned files under `[dry-run]`).
