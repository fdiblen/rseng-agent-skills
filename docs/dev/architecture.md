# Architecture

This page is the big picture: what the repository holds, how the
hand-authored skills are turned into derived artifacts, and what gets
shipped to each AI coding agent. Read it before the per-module details
in [Content pipeline](pipeline.md).

## The core idea

Skill authors hand-write only the distilled guidance
(`skills/<name>/SKILL.md`). Everything factual next to it - the
generated `references.md`, the "Related skills" block, the grouped
skill directory, the README tables, and every per-agent adapter file -
is produced by a Python pipeline from the skills themselves. Each
SKILL.md is the single source of truth for its own topic: its
frontmatter description drives triggering and the adapter renders, and
its curated "Learn more" links drive the generated references. This
keeps the generated material consistent across agents and makes a
content change a mechanical rebuild rather than a manual edit in five
formats.

## Repository layout

```
skills/                 canonical skills (hand-authored + generated refs)
  <name>/SKILL.md       hand-authored distillation (+ generated blocks)
  <name>/references.md  GENERATED from the skill's own Learn-more links
commands/               Claude plugin slash commands (native)
agents/                 Claude plugin subagents (native)
hooks/                  Claude plugin session hooks (enforcement layer)
  gate.py               PreToolUse gate: plan before the first write
  quality_check.py      Stop hook: audit the practice artifact floor
  phase_lib.py          shared state/parsing for the phased hooks
  phase_status.py       UserPromptSubmit one-line phase status
  related_nudge.py      PostToolUse(Skill): surface related skills
  signal_nudge.py       PostToolUse(Write/Edit): file-pattern nudges
  session-context.md    SessionStart context injected into the session
  hooks.json            the hook wiring
  phases.json, related.json, signals.json, clusters.txt  GENERATED
.claude-plugin/         Claude plugin + marketplace manifests (native)
pipeline/               the Python build pipeline (uv project)
  src/rseng_pipeline/     generators, adapter build, checks, utilities
  data/                 url_quarantine.yml (human-flagged URLs)
adapters/templates/     jinja2 templates for non-Claude agents
dist/                   GENERATED per-agent adapter outputs (never committed)
installer/              npm installer that bundles and places content
catalog.yml             external skills catalog (see its own page)
docs/                   this MkDocs Material site
```

Two rules run through the whole tree. First, anything under `dist/`,
every `skills/*/references.md`, the marker-delimited blocks in
`SKILL.md`, `AGENTS.md` and `README.md`, and the JSON data files in
`hooks/` are generated - never hand-edited, safe to delete and
rebuild. Second, Claude is the native target (its files live directly
in `commands/`, `agents/`, `hooks/`, `.claude-plugin/` and `skills/`),
while every other agent is served by a rendered adapter under `dist/`.

## Data flow

```
        skills/<name>/SKILL.md          (hand-authored, canonical)
          |            |
          v            v
 [ references ]   [ related_skills ]
 references.md    "Related skills" block in each SKILL.md
 (from the        + hooks/related.json
 skill's own
 Learn-more       [ skill_directory ]
 links)           directory blocks in AGENTS.md + router skill
          |       + hooks/phases.json, signals.json, clusters.txt
          |
          |       [ readme_skills ]
          |       skills/commands/agents tables + counts in README.md
          |
          v
   [ build_adapters ]
   dist/<target>/  (copilot, cursor, codex, gemini)
   jinja2 templates + canonical skill passthrough + output checks
          |
          v
   Claude reads skills/ natively; other agents read dist/<target>/
          \                         /
           \                       /
            v                     v
             installer bundles skills/ + commands/ + agents/
             + hooks/ + dist/ and places them per agent (npm)
```

Four generators read the skills directly. `references` derives each
skill's `references.md` from the "Learn more (verified)" bullets in its
own SKILL.md. `related_skills` renders the "Related skills" section
into every SKILL.md from a curated relations graph and emits
`hooks/related.json` for the consultation nudge hook. `skill_directory`
rewrites the grouped skill directory in `AGENTS.md` and in the router
skill from a cluster map, and emits `hooks/phases.json`,
`hooks/signals.json` and `hooks/clusters.txt` for the phased
enforcement hooks. `readme_skills` rewrites the marker-delimited
skills, commands and agents tables (and the spelled-out counts) in the
root `README.md`. All four fail loudly on a missing or unknown skill,
so the maps and the `skills/` tree cannot drift apart silently.

## Adapter build

Non-Claude agents (GitHub Copilot, Cursor, Codex CLI, Gemini CLI) cannot
read Claude's plugin natively, so the pipeline renders equivalent files
for them. `build_adapters` assembles one render context from the
canonical sources (each skill's `SKILL.md` frontmatter, the relations
graph in `hooks/related.json`, and the plugin command files) and runs
the jinja2 templates in `adapters/templates/` for each registered
target, writing into `dist/<target>/`. Every target also copies the
canonical `skills/` folders through verbatim, so agents that support
skill-like material read the same bodies Claude does, and ships the
platform-neutral self-check (`rseng-check/rseng_check.py` plus the hooks'
JSON data) that hookless agents are instructed to run before finishing.
After each target renders, two layers of checks run: format-driven
output checks in `checks.py` (size budgets, frontmatter validity,
TOML/JSON validity, placeholder-residue detection) and structural
completeness checks in `build_adapters` itself (every skill, every
command and the self-check must land where that platform reads them).
Any failure fails the build. `dist/` is generated output and is never
committed - it is rebuilt from the skills whenever needed.

## The hooks enforcement layer

`hooks/` is what keeps the skills actively used in a Claude Code
session rather than passively installed. `session-context.md` is
injected at session start; `phase_status.py` keeps the current practice
phase salient on every prompt; `gate.py` blocks the first file write
until a phased practice worklog exists; `related_nudge.py` and
`signal_nudge.py` surface neighbouring skills at the moment a skill is
consulted or a matching file is written; and `quality_check.py` audits
the practice artifact floor once at Stop. The hooks read the generated
`phases.json`, `related.json` and `signals.json`, which is why the
generators above must rerun after skill changes.

## Claude plugin native files

Claude is the first-class target and needs no adapter. Its files are
authored and live in the repository directly:

- `commands/*.md` - the fourteen slash commands (`rseng-check`, `rseng-cite`,
  `rseng-plan`, `rseng-release`, `rseng-reproduce`, `rseng-deps`,
  `rseng-integrity`, `rseng-declare`, `rseng-metrics`, `rseng-digest`,
  `rseng-lesson`, `rseng-onboard`, `rseng-kickoff`, `rseng-panel`) that
  reference skills via `${CLAUDE_PLUGIN_ROOT}`.
- `agents/*.md` - the six subagents (`rseng-auditor`, `rseng-reviewer`,
  `rseng-librarian`, `rseng-scout`, `rseng-compliance-officer`, `rseng-mentor`).
- `hooks/` - the session hooks described above.
- `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` - the
  plugin and marketplace manifests.
- `skills/<name>/SKILL.md` plus the generated `references.md` beside each.

These same command bodies are what the Gemini target translates (replacing
`${CLAUDE_PLUGIN_ROOT}` and `$ARGUMENTS`) so the two agents behave alike.

## Utilities

Beside the generators and the adapter build, the pipeline carries a few
standalone tools: `link_check.py` verifies every external URL in the
generated artifacts (`url_verify.py` does the probing, with the
quarantine list in `pipeline/data/url_quarantine.yml`; `net.py` is the
shared HTTP helper), `rsd_snapshot.py` refreshes the committed Research
Software Directory snapshots inside the `rseng-software-reuse` skill, and
`catalog.py` manages the external skills catalog (`catalog.yml`) - see
[External skills catalog](catalog.md).

## The npm installer

`installer/` is a TypeScript CLI (`rseng-agent-skills`) that places pack content
into a target project for a chosen agent. It never sweeps directories: both
the bundling step and the install step work from explicit whitelists.

- `scripts/prepack.mjs` runs on `npm prepack` and copies a fixed whitelist
  (`skills`, `commands`, `hooks`, `agents`, `dist`, `AGENTS.md`,
  `ATTRIBUTION.md`, `NOTICE`, `LICENSE-content`) from the repository into
  `installer/content/`, so the published package carries the built
  content. It fails loudly if `dist/` is missing, i.e. if the adapter
  build was not run first.
- `src/install.ts` expands a per-agent source whitelist into concrete file
  copies (Claude gets `skills/`, `commands/` and `agents/`, the others get
  their `dist/<target>/` output) and records every installed file with its
  SHA-256 in a `.rseng-agent-skills.json` manifest.
- `src/update.ts` uses that manifest to replace only files the pack still
  owns (on-disk hash still matches), preserving and reporting any file the
  user has edited, and backs up managed files before writing.

## Where to go next

- [Content pipeline](pipeline.md) - module-by-module internals and the
  exact commands to run each stage.
- [Adding a skill](adding-a-skill.md) - the authoring and regeneration
  loop for a new skill.
