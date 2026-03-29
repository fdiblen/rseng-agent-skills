---
description: Draft a Software Management Plan (SMP) skeleton for this project
---

Draft a Software Management Plan for the current repository, following
the practice in
${CLAUDE_PLUGIN_ROOT}/skills/rseng-management-planning/SKILL.md.

Steps:

1. Read the repository first: purpose (README), maturity signals (tests,
   CI, releases, docs, packaging), license, citation files, contributor
   count. Determine the software tier (analysis code / prototype tool /
   infrastructure) - the SMP's depth must match it; a lightweight plan for
   analysis code, a fuller one for infrastructure.
2. Write SMP.md at the repository root (or the path given in $ARGUMENTS)
   with these sections:
   - Purpose and scope: what the software does, for whom, expected lifetime
   - Version control and development workflow
   - Quality: testing, review and CI practice
   - Documentation: user and developer documentation plans
   - Releases and distribution: versioning scheme, channels, cadence
   - Licensing and intellectual property
   - Citation and metadata: CITATION.cff/codemeta, identifiers, credit
   - Maintenance and support: roles, bus factor, dependency policy
   - Preservation and archiving: what is archived where, and when
   - Resources: people, funding and infrastructure the plan relies on
3. Prefill every section with what the repository already shows (state
   the evidence), and mark genuinely open decisions with "[DECIDE: ...]"
   placeholders naming who should decide - do not invent policies,
   funders or commitments.
4. Keep it concise: a page or two for analysis code, at most a few pages
   for infrastructure. Plans that are too long do not get maintained.
5. End the document with a short "Review" line noting the plan should be
   revisited at each major release, and offer 2-3 "Learn more" links taken
   ONLY from rseng-management-planning/references/*/learn-more.md.

Close the generated document with this attribution line, exactly once:

Guidance based on [RSQKit](https://everse.software/RSQKit/) by the EVERSE
project and the RSQKit team, DOI
[10.5281/zenodo.14923573](https://doi.org/10.5281/zenodo.14923573)
(CC-BY-4.0).
