# Content pipeline

The pipeline lives in `pipeline/src/rseng_pipeline/`. It reads the
hand-authored skills (`skills/<name>/SKILL.md`) and derives everything
else: the generated `references.md` beside each skill, the "Related
skills" blocks and the hooks' data files, the grouped skill directory,
the README tables, and the per-agent adapter outputs in `dist/`. This
page documents each module - its job, its inputs and outputs - and the
commands to run each stage.

All commands assume [uv](https://docs.astral.sh/uv/). The pipeline is a uv
project rooted at `pipeline/`, so run modules with
`uv run --directory pipeline python -m rseng_pipeline.<module>`. The
`justfile` at the repo root wraps the common tasks (`just lint`,
`just fix`, `just hooks`).

## Stage order

```
skills/*/SKILL.md
   |
   +--> references        skills/*/references.md
   +--> skill_directory   AGENTS.md + router blocks, hooks/*.json
   +--> related_skills    SKILL.md blocks + hooks/related.json  (LAST)
   +--> readme_skills     README.md tables + counts
   |
   +--> build_adapters    dist/<target>/  (reads frontmatter + commands/)
```

The generators are independent of each other, with one ordering rule:
`related_skills` rewrites a block inside every SKILL.md, so run it last
after anything else that touches skill files. `build_adapters` reads
the skills' frontmatter plus `hooks/related.json`, so regenerate the
relations before an adapter build when they changed:

```
uv run --directory pipeline python -m rseng_pipeline.references
uv run --directory pipeline python -m rseng_pipeline.skill_directory
uv run --directory pipeline python -m rseng_pipeline.related_skills
uv run --directory pipeline python -m rseng_pipeline.readme_skills
uv run --directory pipeline python -m rseng_pipeline.build_adapters
```

## references.py

Generates one `references.md` per skill from that skill's own SKILL.md.
Every skill maintains its verified "Learn more" links inside its body;
this module derives the file beside it so agents have one predictable
place to find vetted pointers. No external content is involved: the
skill file is the single source of truth.

- `extract_curated(skill_md)` pulls the bullets under the
  "Learn more (verified):" marker (both marker spellings accepted,
  wrapped continuation lines joined onto their bullet).
- The generated file carries a do-not-edit header; a skill with no
  curated links gets an explicit "no curated external links" stub
  rather than no file, so the layout is uniform.
- The file is rewritten in full every run, so removed links prune
  automatically.

```
uv run --directory pipeline python -m rseng_pipeline.references
```

## related_skills.py

The skill-relations graph. The map is curated in the module itself
(`RELATED`: skill -> {neighbor: when the neighbor becomes relevant})
and is the single source for two outputs:

- the "Related skills" section rendered between marker comments into
  every SKILL.md (idempotent; rerunning produces the same bytes), and
- `hooks/related.json`, which the `related_nudge.py` hook reads to
  surface neighbours whenever a skill is consulted.

Every skill must have an entry and every edge must name an existing
skill - unknown or missing names fail loudly. Run it as the LAST step
after any content regeneration, since it rewrites skill files.

```
uv run --directory pipeline python -m rseng_pipeline.related_skills
```

## skill_directory.py

One source of truth for "which skill covers what": the cluster map
(`CLUSTERS`), the phase map (`PHASES`: when in a task each practice
area is considered first) and the relevance signals (file patterns that
suggest a skill applies). From those plus each skill's frontmatter
brief it rewrites and emits:

- the grouped skill directory between the skill-directory markers in
  `AGENTS.md` and in `skills/rseng-quality-framework/SKILL.md` (the
  router skill), so the two lists can never drift apart;
- `hooks/phases.json` (phase -> cluster -> skills), `hooks/signals.json`
  the data files behind the phased
  enforcement hooks.

A skill missing from the cluster map fails the run.

```
uv run --directory pipeline python -m rseng_pipeline.skill_directory
```

## readme_skills.py

Regenerates the generated blocks in the root `README.md`: the skills,
commands and agents tables between their markers, and the spelled-out
counts, all from the frontmatter of the actual files. The README never
drifts from the pack contents.

```
uv run --directory pipeline python -m rseng_pipeline.readme_skills
```

## adapters.py

The adapter build framework (not a runnable stage on its own).

- `load_render_context(repo_root)` builds one context dict shared by
  every template: the generated note, the skill entries (name,
  description, scope, brief and related skills - descriptions from each
  `SKILL.md` frontmatter, relations from `hooks/related.json`), and the
  plugin command entries (from `commands/*.md`).
- `template_env(repo_root)` returns a jinja2 `Environment` over
  `adapters/templates/` with `StrictUndefined` (so a missing variable is a
  hard error).
- `copy_skills(repo_root, target_dir)` copies the canonical
  skill folders through verbatim (used by the unified tree and the
  Gemini bundle).
- `build_command_skills(context, target_dir)` renders each plugin
  command (minus `CLAUDE_ONLY_COMMANDS`, currently `rseng-panel`) as an
  explicitly-invoked skill: a `SKILL.md` carrying
  `disable-model-invocation: true` in its frontmatter plus an
  `agents/openai.yaml` that disables implicit invocation for Codex.
- `build_agents_skills(repo_root, context, target_dir)` assembles the
  unified native tree `.agents/skills/` - every canonical skill copied
  through plus the command-skills - which Codex, Cursor and Copilot
  all read natively.
- `copy_check(repo_root, target_dir)` ships the platform-neutral
  self-check (`rseng_check.py` plus the hooks' `phases.json`,
  `related.json` and `signals.json`) next to a target's context files;
  hookless agents are instructed to run it before finishing.
- `render_to(...)` renders one template to one output path.
- `TARGETS` plus the `@target(name)` decorator form the registry that
  concrete targets register into. The target modules live in
  `targets/` (`copilot`, `cursor`, `codex`, `gemini`); importing the
  package registers them all.

## build_adapters.py

Builds every registered adapter target into `dist/`.

- `build(repo_root, only=None)` loads the render context and template
  environment, then for each target wipes and recreates `dist/<target>/`,
  calls the target's build function, and runs two layers of validation
  on the result: the format-driven output checks (`check_target` in
  `checks.py`) and a static structural check that every skill, every
  command-skill and the self-check actually landed where that platform
  reads them. Any problem aborts the build with `SystemExit`.

Run it (all targets, or a subset):

```
uv run --directory pipeline python -m rseng_pipeline.build_adapters
uv run --directory pipeline python -m rseng_pipeline.build_adapters copilot gemini
```

The per-target modules define the output layout. Copilot, Cursor and
Codex all emit the same unified native tree, `.agents/skills/`
(via `build_agents_skills`): every canonical skill folder verbatim
plus the generated command-skills. On top of that each renders one
thin context file carrying the behavior rules - Copilot
`.github/copilot-instructions.md`, Cursor a single always-on
`.cursor/rules/rseng-overview.mdc` rule, Codex a size-checked
`AGENTS.md` that also carries the compact full skill inventory
(Codex's native startup skills listing has a context budget and may
truncate). Gemini keeps its extension layout: a manifest, `GEMINI.md`,
TOML commands translated from the Claude command bodies, and a
`skills/` passthrough. Each target also carries the `rseng-check/`
self-check folder.

## checks.py

Post-render validation run by `build_adapters` after each target renders; a
non-empty problem list fails the build. Checks are format-driven:

- Character/byte budgets for whole-file context docs
  (`copilot-instructions.md` 16 KiB, `GEMINI.md` 24 KiB, `AGENTS.md`
  32 KiB).
- Required frontmatter fields for `.instructions.md`
  (`description`, `applyTo`) and `.mdc` (`description`, `alwaysApply`).
- TOML validity plus required `description`/`prompt` for Gemini commands;
  JSON validity for `.json` files.
- Residue checks: a leaked `CLAUDE_PLUGIN_ROOT` placeholder, or unrendered
  template/Liquid `{%` markers in `.md`/`.mdc` files.

Canonical passthrough content (`SKILL.md` and `references.md`) is
skipped here - it is validated at its source, not per adapter.

## link_check.py

Checks every external URL in the generated artifacts. It scans `dist/`
and the generated `skills/*/references.md` files for http(s) URLs,
verifies each distinct URL once (quarantine list respected, HEAD with a
GET fallback, parallel probes) and reports. Broken links fail the run;
quarantined links are skipped by design; network errors are warnings so
a flaky resolver cannot redden CI on its own.

```
uv run --directory pipeline python -m rseng_pipeline.link_check
```

## url_verify.py and net.py

`url_verify` verifies external URLs before they are propagated into
generated content. The quarantine list
(`pipeline/data/url_quarantine.yml`) holds URLs a human has flagged;
those are rejected without probing. Everything else gets an HTTP HEAD
probe with a GET fallback for servers that refuse HEAD. The probe
function is injectable so callers and tests can run without network
access. `net.py` is the minimal shared HTTP helper used by the online
modules.

## rsd_snapshot.py

Snapshots software catalogs from Research Software Directory instances
into compact, committed JSON files (one per instance) under
`skills/rseng-software-reuse/data/`, so agents can suggest existing
research software directly, without a live query. Entries carry keywords
and programming languages so suggestions can match on domain and stack.
Refreshed explicitly, never during normal builds.

```
uv run --directory pipeline python -m rseng_pipeline.rsd_snapshot
```

## catalog.py

Manages the external-skills catalog (`catalog.yml` at the repository
root) with `list`, `check` and `stage` subcommands - see
[External skills catalog](catalog.md).

## How the pipeline is verified

There is no unit-test suite. Every generator is deterministic and its
output is committed, so the check that matters is regenerating and
diffing: if a change alters what a generator produces, the committed file
no longer matches and CI fails. `validate.yml` runs each generator and
then `git diff --exit-code`.

Run the same thing locally:

```
uv run --directory pipeline python -m rseng_pipeline.references
uv run --directory pipeline python -m rseng_pipeline.related_skills
uv run --directory pipeline python -m rseng_pipeline.skill_directory
uv run --directory pipeline python -m rseng_pipeline.readme_skills
uv run --directory pipeline python -m rseng_pipeline.build_adapters
git diff --exit-code
```

`skill_lint`, `token_budget` and `catalog check` are the other gates.
Lint and format with `just lint` / `just fix` (ruff), and install the
pre-commit hooks with `just hooks`.

The agent-in-the-loop harness that used to live here now has its own
project, rseng-agent-skills-scenarios, which drives real agent sessions
against this pack and reports on what they produced.
