---
description: Pre-submission integrity battery for manuscript and results
---

Run the pre-submission integrity battery, following
${CLAUDE_PLUGIN_ROOT}/skills/rseng-research-integrity/SKILL.md. If
$ARGUMENTS names a manuscript file, use it; otherwise locate the
manuscript or result-bearing documents in the repository.

Steps:

1. Internal statistics: statcheck-style recomputation of reported
   test statistics, GRIM-style granularity checks, page arithmetic
   (totals, percentages, subgroup Ns).
2. Regeneration: run the pipeline and compare every reported number,
   table and figure value against fresh outputs within stated
   rounding.
3. Citations: verify every reference resolves and matches its claim,
   and screen all DOIs against the Retraction Watch data
   (rseng-citation-hygiene, rseng-fact-checking).
4. Availability statements: every "available at" link resolves and
   matches (rseng-archiving, rseng-reproducibility).
5. Declarations: contributions, AI use (aidecl.yaml current) and
   conflicts as the venue requires.
6. Report findings with locations and severities, framed as
   proofreading, not accusation; write the report into the project
   record and fix what the user approves.

Follow each skill's attribution guidance in what you produce.
