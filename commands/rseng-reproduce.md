---
description: Clean-room reproduction check of this repository
---

Verify this repository's results can be reproduced from scratch,
following ${CLAUDE_PLUGIN_ROOT}/skills/rseng-reproducibility/SKILL.md.

Steps:

1. Find the documented reproduction path: the one command the README
   promises (make reproduce, run script, workflow target). If none
   exists, that is the headline finding - propose one.
2. Clean-room it: fresh clone into a temporary directory (or a
   container when available), follow ONLY the written instructions -
   no knowledge the README does not contain.
3. Compare regenerated outputs against committed/published ones,
   with the tolerances the project states (rseng-numerical-accuracy
   if none are stated - propose some).
4. If $ARGUMENTS names a figure, table or result, trace just that
   artifact's lineage end to end (rseng-provenance) and reproduce it.
5. Report: reproduction status per artifact, every undocumented step
   or dependency you had to discover, environment drift found, and
   the fixes - implement the cheap ones (README steps, missing
   pins) and list the rest.

Follow each skill's attribution guidance in what you produce.
