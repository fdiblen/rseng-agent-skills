# Adding a skill

A skill is one hand-authored `skills/rseng-<topic>/SKILL.md` plus a
pipeline-generated `references.md` beside it. Skills are the canonical
content; every adapter is derived from them. Adding one is mostly
editorial work (the body and its curated links) followed by a
regeneration and validation loop that is entirely mechanical.

## 1. Author SKILL.md

Create `skills/rseng-<topic>/SKILL.md` and follow the authoring template at
[Skill authoring template](skill-authoring-template.md) - it is the source
of truth for the frontmatter fields, the body structure (overview,
guidance sections, `## Working with this skill`, the curated
"Learn more (verified)" links) and the hard constraints (body <= 500
lines, plain ASCII, no unverified
URLs). Do not restate those rules here; read the template.

The skill name (`rseng-<topic>`) is a stable identifier - installs key off
it, so it must not change casually.

### Make the description trigger distinct

The `description` is what every agent uses to decide when to load the
skill, so it has to be distinguishable from its siblings. Read the
neighbouring `SKILL.md` descriptions before writing yours, and make sure
the trigger conditions do not overlap. Cover both everyday phrasing and
domain terms a user might use (the template calls this out: "write
tests" as well as "CI matrix"). This is the cross-review pass the
template refers to - a description that could equally match
`rseng-testing` and `rseng-ci-cd` will cause the wrong skill to fire.

## 2. Register the skill in the curated maps

Two pipeline modules keep curated maps that must know every skill; both
fail loudly on a missing entry, so the build tells you if you forget:

- `pipeline/src/rseng_pipeline/skill_directory.py` - add the skill to the
  `CLUSTERS` map (which practice cluster it belongs to) and, if a file
  pattern in a project signals that the skill applies, to the relevance
  signals.
- `pipeline/src/rseng_pipeline/related_skills.py` - add an entry to the
  `RELATED` map: for each neighbouring skill, one short line saying when
  that neighbour becomes relevant. Add the reverse edges on the
  neighbours too, where they make sense.

## 3. Regenerate

`references.md`, the directory blocks, the "Related skills" sections and
the README tables are generated and never hand-edited. After the
SKILL.md and the map entries are in place, rebuild them (relations last,
since that step rewrites skill files):

```
uv run --directory pipeline python -m rseng_pipeline.references
uv run --directory pipeline python -m rseng_pipeline.skill_directory
uv run --directory pipeline python -m rseng_pipeline.related_skills
uv run --directory pipeline python -m rseng_pipeline.readme_skills
```

This writes the new skill's `references.md` from its curated
"Learn more" links, adds it to the grouped directory in `AGENTS.md` and
the router skill, renders its "Related skills" block, refreshes the
hooks' data files (`hooks/phases.json`, `related.json`, `signals.json`,
`clusters.txt`) and updates the README tables and counts.

## 4. Rebuild the adapters

Every non-Claude target is rendered from the skills, so regenerate them so the
new skill flows into Copilot, Cursor, Codex and Gemini outputs:

```
uv run --directory pipeline python -m rseng_pipeline.build_adapters
```

This rebuilds `dist/<target>/` from scratch and runs the post-render checks
(`checks.py`) plus the structural completeness checks on each output; a
check failure fails the build. `dist/` is generated and not committed.
If you are adding an entirely new agent target rather than a skill, see
[Adding an adapter](adding-an-adapter.md).

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

- One commit for the hand-authored `SKILL.md` and the map entries in
  `skill_directory.py` / `related_skills.py`.
- A separate commit for the regenerated artifacts (`references.md`, the
  directory and relations blocks, the hooks data, the README tables);
  they are mechanical, and keeping them apart makes the authored change
  reviewable on its own.

Do not fold unrelated formatting or other skills' files into the same commit.
The generated `dist/` is not committed, so it does not appear in your diff.
