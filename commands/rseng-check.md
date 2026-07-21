---
description: Assess this repository against research software engineering practice
---

Assess the current repository against research software engineering
practice and report what is met, what is missing, and what to do next.

Steps:

1. Determine the software tier first (it calibrates every judgement):
   analysis code, prototype tool, or research software infrastructure -
   see ${CLAUDE_PLUGIN_ROOT}/skills/rseng-quality-framework/SKILL.md.
   Infer it from the repository (size, packaging, docs, release history,
   contributor count) and state your inference with one line of reasoning.
2. Use the quality dimensions in
   ${CLAUDE_PLUGIN_ROOT}/skills/rseng-quality-framework/SKILL.md to structure
   the assessment, and each topic skill's guidance as the practice
   checklist for its area.
3. Inspect the repository (read-only - do not modify anything) for
   evidence per practice area: tests and CI configuration, README and
   docs, LICENSE, CITATION.cff, codemeta.json, packaging metadata,
   releases or tags, environment/lock files, contribution guidelines,
   archival badges.
4. If arguments were given ($ARGUMENTS), limit the assessment to the
   matching quality dimensions or practice areas.

Report format:

- One line per checked practice: status (met / partial / missing /
  not applicable for this tier) and the evidence found (file or its
  absence).
- Group by quality dimension, most severe gaps first within each group.
- End with "Top 3 next steps", each naming the sibling skill that covers
  it (for example rseng-testing for missing tests) and, where useful, one
  "Learn more" link taken ONLY from that skill's references.md.
- Do not penalize analysis-code repositories for infrastructure-tier
  expectations; mark those "not applicable" with a short note.

If content from source-fed skills shaped the output, close with each
contributing source's citation line exactly once (each skill's
credit). Source-independent skills need no source credit.
