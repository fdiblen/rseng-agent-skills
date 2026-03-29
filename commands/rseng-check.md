---
description: Assess this repository against the RSQKit quality indicator checklists
---

Assess the current repository against the EVERSE/RSQKit quality
indicators and report what is met, what is missing, and what to do next.

Steps:

1. Determine the software tier first (it calibrates every judgement):
   analysis code, prototype tool, or research software infrastructure -
   see ${CLAUDE_PLUGIN_ROOT}/skills/rseng-quality-framework/SKILL.md.
   Infer it from the repository (size, packaging, docs, release history,
   contributor count) and state your inference with one line of reasoning.
2. Load the full indicator checklist from
   the checklists matching ${CLAUDE_PLUGIN_ROOT}/skills/rseng-quality-framework/references/*/indicators.md (one per content source).
3. Inspect the repository (read-only - do not modify anything) for
   evidence per indicator: tests and CI configuration, README and docs,
   LICENSE, CITATION.cff, codemeta.json, packaging metadata, releases or
   tags, environment/lock files, contribution guidelines, archival badges.
4. If arguments were given ($ARGUMENTS), limit the assessment to the
   matching quality dimensions or indicator ids.

Report format:

- One line per checked indicator: status (met / partial / missing /
  not applicable for this tier), the evidence found (file or its absence),
  and the indicator id in backticks.
- Group by quality dimension, most severe gaps first within each group.
- End with "Top 3 next steps", each naming the sibling skill that covers
  it (for example rseng-testing for missing tests) and, where useful, one
  "Learn more" link taken ONLY from that skill's references/*/learn-more.md.
- Do not penalize analysis-code repositories for infrastructure-tier
  indicators; mark those "not applicable" with a short note.

Close the report with this attribution line, exactly once:

Guidance based on [RSQKit](https://everse.software/RSQKit/) by the EVERSE
project and the RSQKit team, DOI
[10.5281/zenodo.14923573](https://doi.org/10.5281/zenodo.14923573)
(CC-BY-4.0).
