# Taxonomy

`extensions/rsqkit/taxonomy.yml` is the contract between upstream RSQKit content and
the skills in this pack. It maps every upstream page to exactly one skill,
and it is what the generated `references/` folders and the per-agent
adapters are derived from. If you change which pages a skill covers, you
change this file - not the generated output.

## Structure

The file has a single top-level `skills:` mapping. Each key is a skill name
(matching a `skills/<name>/` directory), and each value has:

- `scope` - a prose description of what the skill covers. Used verbatim in
  the adapter render context (Copilot/Cursor/Codex/Gemini) as the skill's
  scope line.
- `pages` - the task page_ids the skill owns.
- `concept_pages` - (optional) framework/concept page_ids.
- `role_pages` - (optional) role page_ids.

Only `rseng-quality-framework` uses `concept_pages` and `role_pages`; it is
the router skill and owns all the concept and role pages but no task page.
Every other skill uses `pages` only. A minimal example:

```yaml
skills:
  rseng-testing:
    scope: >-
      Writing and running software tests: test types and levels, testing
      frameworks, coverage, and managing complex CI testing matrices.
    pages:
      - testing_software
      - ci_testing_matrices
```

In code, `references.skill_page_ids(entry)` is the canonical reader: it
concatenates `pages + concept_pages + role_pages` into the full list of
page_ids a skill maps. Both the references generator and the adapter build
call it, so the three keys are equivalent as far as "which pages belong to
this skill" is concerned - the split only signals intent (task vs concept
vs role).

## The exactly-once rule

Every task, concept, and role page at the pinned upstream commit must appear
exactly once across all skills' `pages`, `concept_pages`, and `role_pages`.
This is what makes the taxonomy a partition of the upstream content rather
than an arbitrary selection:

- A page mapped to no skill would be silently dropped from the pack.
- A page mapped to two skills would be duplicated and its guidance split.

The pipeline enforces one half of this directly: in
`references.generate_references`, every mapped `page_id` must have a
matching fragment in `build/fragments/`, or the build raises
`FileNotFoundError: <skill>: no fragment for page_id <id>`. That catches a
page_id in the taxonomy that upstream does not (or no longer) provides. The
other half - upstream pages that exist but are mapped nowhere - is checked
by the sync tooling that compares the pinned upstream page set against the
taxonomy when the pin is bumped.

## page_id is the key, not the filename

The pipeline keys everything on the frontmatter `page_id`, never the upstream
filename. `parser.load_pages` reads each `cache/pages/**/*.md`, parses its
frontmatter, and stores the record under its `page_id`. The fragment written
by the assembler is named `<page_id>.md`, and the taxonomy lists `page_id`s.
So an upstream file whose name differs from its `page_id` flows through
correctly as long as the taxonomy uses the `page_id`.

There are three such mismatches at the pinned commit. In each case the
taxonomy (and every generated artifact) uses the right-hand `page_id`:

| Upstream filename                    | Frontmatter page_id (used here) |
| ------------------------------------ | ------------------------------- |
| `writing_research_software_stories.md` | `writing_research_software_story` |
| `software_project_structure.md`      | `structuring_software_projects` |
| `software_maintenance.md`            | `maintaining_research_software` |

If you are hunting for the upstream source of one of these skills' pages,
look for the filename on the left; if you are editing the taxonomy or a
skill's `source_pages`, use the `page_id` on the right.

## How references and adapters derive from it

Both consumers read `taxonomy.yml` through `load_taxonomy` /
`skill_page_ids` and stay in lockstep with it:

- References (`references.generate_references`): for each skill it copies
  `references/pages/<page_id>.md` for every mapped page, and builds
  `references/tools.md`, `references/learn-more.md`, and
  `references/indicators.md` restricted to those pages. Each skill's folder
  is wiped and rebuilt every run, so removing a page from the taxonomy
  prunes it from the generated output automatically.
- Adapters (`adapters.load_render_context` -> `_skill_entries`): for each
  skill it emits `name`, `description` (from the skill's `SKILL.md`
  frontmatter), `scope` (from the taxonomy), and the list of mapped pages
  with their titles and canonical RSQKit URLs (from `build/content.json`).
  The jinja2 templates in `adapters/templates/` turn that into each agent's
  files.

Because both paths derive from the same mapping, the taxonomy is the one
place to change coverage. Edit it, then rebuild
(`references` and `build_adapters`); do not hand-edit anything under
`skills/*/references/` or `dist/`.

## Keeping a skill's frontmatter in sync

Each `skills/<name>/SKILL.md` carries a `metadata.source_pages` list in its
frontmatter that should match the skill's page_ids in the taxonomy. The
taxonomy is authoritative for what the pipeline generates; `source_pages` is
the human-facing record next to the hand-written body. When you change a
skill's pages, update both. See the
[skill authoring template](skill-authoring-template.md) for the full
frontmatter contract.
