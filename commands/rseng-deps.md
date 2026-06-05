---
description: Audit this project's dependencies on all six axes
---

Audit every dependency of this project, following
${CLAUDE_PLUGIN_ROOT}/skills/rseng-dependency-management/SKILL.md.

Steps:

1. Enumerate the full tree from the lockfiles/manifests (direct and
   transitive); no lockfile is itself a top finding.
2. Per dependency check the six axes: suitability (still used?
   smallest tool for the job?), license compatibility including the
   tree (rseng-license-compliance), known vulnerabilities first and
   second degree (osv.dev / deps.dev), documentation, maintenance
   signals, and currency - versions behind latest, end-of-life
   runtimes (endoflife.date).
3. If $ARGUMENTS names a package, vet just that candidate in depth
   (intake mode).
4. Report as a table: dependency, axes passed/failed, severity,
   recommended action (update / replace / remove / accept with
   reason). Implement the safe updates (patch/minor with green
   tests) if the user confirms; record accepted risks in the
   decision log.

Follow each skill's attribution guidance in what you produce.
