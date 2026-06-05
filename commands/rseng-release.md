---
description: Run the pre-release checklist and prepare the release
---

Prepare this repository for a release, following
${CLAUDE_PLUGIN_ROOT}/skills/rseng-publishing-releasing/SKILL.md and its
sibling skills. If $ARGUMENTS names a version, use it; otherwise
propose the next version from the change history and semantic
versioning.

Steps:

1. Verify the tree is releasable: tests green, working tree clean,
   CI passing on the release branch.
2. Version and changelog: bump consistently everywhere the version
   appears; distill the changelog entry from commits since the last
   tag (human-readable, breaking changes first).
3. Currency checks: CITATION.cff and codemeta.json match reality
   (version, DOI placeholder, contributors - run the contributor
   diff from rseng-citation-metadata); README install/quickstart still
   true; aidecl.yaml up to date (rseng-ai-declaration).
4. Obligations: license obligations of shipped dependencies satisfied
   (rseng-license-compliance); no sensitive files in the artifact
   (rseng-security).
5. Archive wiring: forge-to-Zenodo integration or deposit plan, and a
   Software Heritage save request at tag time (rseng-archiving).
6. Report what is ready, what you fixed, and what needs a human
   decision (registry publication and any push/publish step ALWAYS
   needs explicit approval - never publish autonomously).

Follow each skill's attribution guidance in what you produce.
