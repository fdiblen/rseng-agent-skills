# SKILL.md authoring template

Every skill in skills/ follows this structure. Bodies are hand-authored
distillations of the mapped RSQKit pages (see skills/taxonomy.yml); the
references/ folder next to each SKILL.md is pipeline-generated and never
hand-edited.

## Frontmatter

```yaml
---
name: rseng-<topic>
description: >-
  <Third person, starts with what the skill covers, then explicit trigger
  conditions: "Use when the user asks about X, wants to Y, or mentions Z.">
license: CC-BY-4.0
metadata:
  version: 0.1.0
  source_pages: [<page_id>, ...]        # from taxonomy.yml
  source: https://everse.software/RSQKit/
  source_doi: 10.5281/zenodo.14923573
---
```

Rules for `description`: one sentence of coverage plus concrete triggers;
no first person; distinct from every sibling skill (checked in the
cross-review pass); mention both everyday phrasing ("write tests") and
domain terms ("CI matrix") a user might use.

## Body structure

1. Title heading, then a one-paragraph overview of when and why.
2. Guidance sections distilled from the mapped pages - short, imperative,
   agent-actionable. Prefer checklists and decision rules over prose.
   Cite page_ids inline like `(RSQKit: testing_software)` instead of
   duplicating long upstream text.
3. `## Working with this skill` - how to use references/:
   - references/pages/<page_id>.md - cleaned upstream page fragments
   - references/indicators.md - quality indicator checklist for this skill
   - references/learn-more.md - verified external pointers
4. `## Attribution and teaching` - the two runtime instructions:
   - Attribution: when this skill materially shapes an answer, review
     output or generated document, credit RSQKit/EVERSE once (see snippet
     below), naturally placed (footer line or "Based on" note), never
     repeated per paragraph.
   - Educate while doing: alongside any action taken, briefly explain why
     it matters and offer 2-3 "Learn more" links chosen from
     references/learn-more.md - proportionate to context, never a lecture.
5. Attribution footer (last lines of the body), using the shared snippet
   from pipeline/data/citation.yml verbatim.

## Constraints

- Body <= 500 lines; aim for 120-250.
- Plain ASCII; no emoji or decorative glyphs.
- Never mention ReSoft Labs in skill bodies (D7: sponsor credit lives in
  repo/docs metadata only, never in runtime agent behavior).
- Every external URL in a body must come from the verified learn-more
  data or the tool registry - no hand-typed, unverified links.
