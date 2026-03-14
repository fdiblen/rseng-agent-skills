# Adding a skill

A skill is one hand-authored `skills/rseng-<topic>/SKILL.md` plus a
pipeline-generated `references/` folder beside it. Skills are the canonical
content; every adapter is derived from them. Adding one is mostly editorial
work (the taxonomy mapping and the body) followed by a regeneration and
validation loop that is entirely mechanical.

The contract that ties a skill to upstream is `skills/taxonomy.yml`: it maps
RSQKit page_ids to skills, and `references/` folders, adapters and sync impact
reports are all derived from it. A page_id that does not appear in the taxonomy
is not part of any skill; a page_id that appears twice breaks the "exactly
once" rule the taxonomy header states.

## 1. Map the upstream pages in taxonomy.yml

Open `skills/taxonomy.yml` and add an entry under `skills:`. The key is the
skill name (`rseng-<topic>`, a stable identifier - installs key off it, so it
must not change casually). An entry has a `scope` and up to three page lists:

- `pages` - task pages (the how-to content a skill is built around)
- `concept_pages` - framework/concept pages
- `role_pages` - role entry-point pages

Only `rseng-quality-framework` uses `concept_pages` and `role_pages` today;
most topic skills use `pages` only. Follow the shape of an existing entry:

```yaml
  rseng-testing:
    scope: >-
      Writing and running software tests: test types and levels, testing
      frameworks, coverage, and managing complex CI testing matrices across
      compilers, platforms and dependencies.
    pages:
      - testing_software
      - ci_testing_matrices
```

The page_ids must be **true upstream page_ids** - the basename of a page under
the source paths listed in `pipeline/upstream.lock` (`pages/tasks/`,
`pages/roles/`, `pages/research_software_and_quality/`). The pipeline resolves
each page_id against the assembled `content.json`; a page_id with no matching
upstream fragment fails the reference build with
`no fragment for page_id '<id>'` (see `references.py`,
`generate_references`). Every task, concept and role page at the pinned commit
must appear exactly once across all skills - if you are adding a skill to cover
pages that another skill currently owns, move them, do not duplicate them.

## 2. Author SKILL.md

Create `skills/rseng-<topic>/SKILL.md` and follow the authoring template at
[Skill authoring template](skill-authoring-template.md) - it is the source of
truth for the frontmatter fields, the body structure (overview, guidance
sections citing page_ids inline, `## Working with this skill`,
`## Attribution and teaching`, attribution footer) and the hard constraints
(body <= 500 lines, plain ASCII, no ReSoft Labs mention in the body, no
hand-typed URLs). Do not restate those rules here; read the template.

Two frontmatter fields couple back to step 1 and to the generated references:

- `metadata.source_pages` must list the same page_ids you put in the taxonomy
  entry. Keep them in sync by hand.
- The body cites page_ids inline (for example `(RSQKit: testing_software)`)
  rather than pasting upstream prose; the full text lives in the generated
  `references/pages/<page_id>.md`.

### Make the description trigger distinct

The `description` is what every agent uses to decide when to load the skill,
so it has to be distinguishable from its siblings. Read the sibling entries in
`skills/taxonomy.yml` and the neighbouring `SKILL.md` descriptions before
writing yours, and make sure the trigger conditions do not overlap. Cover both
everyday phrasing and domain terms a user might use (the template calls this
out: "write tests" as well as "CI matrix"). This is the cross-review pass the
template refers to - a description that could equally match `rseng-testing`
and `rseng-ci-cd` will cause the wrong skill to fire.

## 3. Regenerate references

`references/` is generated and never hand-edited. After the taxonomy and
SKILL.md are in place, rebuild it:

```
uv run --directory pipeline python -m rseng_pipeline.references
```

This wipes and rewrites `references/` for every skill from the build
artifacts, so a removed page prunes automatically and a new skill gets its
folder populated. It writes, per skill: `references/pages/<page_id>.md` (one
cleaned fragment per mapped page), `references/tools.md`, `references/learn-more.md`
and `references/indicators.md`. If it raises `no fragment for page_id ...`, the
page_id in your taxonomy entry does not exist at the pinned commit - fix the
id (or the pin) rather than the generator.

The reference build reads `pipeline/build/` (content.json and fragments),
which the assembler produces from the fetched upstream cache. If `build/` is
stale or absent, run the assembler first, exactly as the publish workflow does:

```
uv run --directory pipeline python -m rseng_pipeline.assembler
uv run --directory pipeline python -m rseng_pipeline.references
```

## 4. Rebuild the adapters

Every non-Claude target is rendered from the skills, so regenerate them so the
new skill flows into Copilot, Cursor, Codex and Gemini outputs:

```
uv run --directory pipeline python -m rseng_pipeline.build_adapters
```

This rebuilds `dist/<target>/` from scratch and runs the post-render checks
(`checks.py`) on each output; a check failure fails the build. `dist/` is
generated and not committed. If you are adding an entirely new agent target
rather than a skill, see [Adding an adapter](adding-an-adapter.md).

## 5. Validate

- `claude plugin validate` on the plugin root - the skill must be discoverable
  and its frontmatter well-formed. The plugin manifest advertises a skill
  count (`.claude-plugin/plugin.json` / `marketplace.json`); update the count
  wording there if you changed the number of skills.
- Confirm the adapter build passed its checks (step 4) - that is the automated
  gate on size budgets, required frontmatter and placeholder leaks for the
  generated outputs.
- Re-read your `description` against the siblings one more time for trigger
  distinctness - this is the check no tool performs for you.

## 6. Commit

Keep commits small and focused, matching the repository's existing history:

- One commit for the `taxonomy.yml` mapping and the hand-authored `SKILL.md`.
- A separate commit for the regenerated `references/` (it is a mechanical
  artifact; keeping it apart makes the authored change reviewable on its own).

Do not fold unrelated formatting or other skills' files into the same commit.
The generated `dist/` is not committed, so it does not appear in your diff.
