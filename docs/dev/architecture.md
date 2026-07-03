# Architecture

This page is the big picture: what the repository holds, where content
comes from, how it is transformed, and what gets shipped to each AI coding
agent. Read it before the per-module details in
[Content pipeline](pipeline.md) or the contract in [Taxonomy](taxonomy.md).

## The core idea

Skill authors hand-write only the distilled guidance
(`skills/<name>/SKILL.md`). Everything factual next to it - the generated
`references.md`, and every per-agent adapter file - is produced by a
Python pipeline. Source-fed content derives from pinned snapshots of the
installed content sources (each extension under `extensions/` pins one
upstream repository at one commit); most skills are source-independent
and carry their own curated links. This keeps provenance auditable (one
commit hash per source), keeps the generated material consistent across
agents, and lets an upstream refresh be a mechanical rebuild rather than
a manual edit.

## Repository layout

```
skills/                 canonical skills (hand-authored + generated refs)
  <name>/SKILL.md       hand-authored distillation
  <name>/references.md  GENERATED source links + learn-more pointers
extensions/             one folder per content source (rsqkit, nlesc-guide)
  <source>/source.yml   name, title, base URL, DOI, content license
  <source>/upstream.lock       the source's pinned repo/ref/commit
  <source>/upstream.manifest.json  per-file SHA-256 at the pin
  <source>/taxonomy.yml the contract: page_id -> skill mapping
  <source>/data/        curated inputs (citation, quarantine, learn-more)
pipeline/               the Python content pipeline (source-agnostic engine)
  src/rseng_pipeline/  fetch -> parse -> clean -> verify -> assemble -> refs
  cache/<source>/       downloaded upstream files + manifest.json (generated)
  build/<source>/       content.json + fragments/ (generated)
adapters/templates/     jinja2 templates for non-Claude agents
commands/               Claude plugin slash commands (native)
agents/                 Claude plugin subagents (native)
.claude-plugin/         Claude plugin + marketplace manifests (native)
dist/                   GENERATED per-agent adapter outputs (never committed)
installer/              npm installer that bundles and places content
docs/                   this MkDocs Material site
```

Two rules run through the whole tree. First, anything under `cache/`,
`build/`, `skills/*/references.md`, and `dist/` is generated - never
hand-edited, safe to delete and rebuild. Second, Claude is the native
target (its files live directly in `commands/`, `agents/`,
`.claude-plugin/` and `skills/`), while every other agent is served by a
rendered adapter under `dist/`.

## The pinned upstreams

Each content source pins exactly one upstream repository, ref, and
commit in its `extensions/<source>/upstream.lock` (a TOML file), plus
the source paths and data globs the pipeline is allowed to consume.
Nothing else decides what upstream content enters the pack. The sync
workflow updates these pins; they are not meant to be edited by hand.
Because each commit hash is fixed, every generated artifact can carry
that hash in its header, so any fragment traces back to an exact
upstream state of its source.

## Data flow

```
  extensions/<source>/upstream.lock          (one per content source)
          |
          v
   [ fetch ]  download pinned files -> pipeline/cache/<source>/ (+ manifest.json)
          |
          v
   [ parse ]  markdown + frontmatter -> normalized PageRecord (keyed by page_id)
          |
          v
   [ clean ]  Liquid/tool-tags/site-links -> portable markdown fragments
          |
          v
 [ verify URLs ]  HEAD/GET probe + quarantine list -> keep only reachable links
          |
          v
 [ learn-more ]  per-page external + curated pointers (merged from data/)
          |
          v
 [ assemble ]  pipeline/build/<source>/content.json + .../fragments/<page_id>.md
          |
          +-------------------------+
          v                         v
 [ references ]             [ build_adapters ]
 skills/<name>/references.md dist/<target>/ (copilot, cursor, codex, gemini)
 (per taxonomy.yml)          (jinja2 templates + canonical skill passthrough)
          |                         |
          v                         v
  Claude reads skills/       other agents read dist/<target>/
          \                         /
           \                       /
            v                     v
             installer bundles skills/ + dist/
             and places them per agent (npm)
```

`fetch` through `assemble` is one linear content pipeline, run once per
installed content source, ending at that source's build artifacts.
`references` and `build_adapters` are two independent consumers of those
artifacts: the first writes each skill's generated `references.md` (one
section per source; source-independent skills get theirs derived from
the curated links in their own SKILL.md), the second renders the
non-Claude adapter outputs into `dist/`. Both are driven by each
source's `extensions/<source>/taxonomy.yml` mapping.

## Adapter build

Non-Claude agents (GitHub Copilot, Cursor, Codex CLI, Gemini CLI) cannot
read Claude's plugin natively, so the pipeline renders equivalent files for
them. `build_adapters` assembles one render context from the canonical
sources (each extension's `taxonomy.yml`, `build/<source>/content.json`
and `data/citation.yml`, each
skill's `SKILL.md` frontmatter, and the plugin command files) and runs the
jinja2 templates in `adapters/templates/` for each registered target,
writing into `dist/<target>/`. Several targets also copy the canonical
`skills/` folders through verbatim, so agents that support skill-like
material still read the same bodies Claude does. After each target renders,
format-driven checks run (size budgets, frontmatter validity, TOML/JSON
validity, placeholder-residue detection); any failure fails the build.
`dist/` is generated output and is never committed - it is rebuilt from the
pinned content whenever needed.

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
- `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` - the
  plugin and marketplace manifests.
- `skills/<name>/SKILL.md` plus the generated `references.md` beside each.

These same command bodies are what the Gemini target translates (replacing
`${CLAUDE_PLUGIN_ROOT}` and `$ARGUMENTS`) so the two agents behave alike.

## The npm installer

`installer/` is a TypeScript CLI (`rseng-agent-skills`) that places pack content
into a target project for a chosen agent. It never sweeps directories: both
the bundling step and the install step work from explicit whitelists.

- `scripts/prepack.mjs` runs on `npm prepack` and copies a fixed whitelist
  (`skills`, `dist`, `AGENTS.md`, `ATTRIBUTION.md`, `NOTICE`,
  `LICENSE-content`) from the repository into `installer/content/`, so the
  published package carries the built content. It fails loudly if `dist/`
  is missing, i.e. if the adapter build was not run first.
- `src/install.ts` expands a per-agent source whitelist into concrete file
  copies (Claude gets `skills/`, the others get their `dist/<target>/`
  output) and records every installed file with its SHA-256 in a
  `.rseng-agent-skills.json` manifest.
- `src/update.ts` uses that manifest to replace only files the pack still
  owns (on-disk hash still matches), preserving and reporting any file the
  user has edited, and backs up managed files before writing.

## Where to go next

- [Content pipeline](pipeline.md) - module-by-module internals and the
  exact commands to run each stage.
- [Taxonomy](taxonomy.md) - the `page_id`-to-skill contract that drives the
  references and adapter builds.
