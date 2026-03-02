---
description: Generate CITATION.cff and codemeta.json for this repository
---

Create or update citation metadata for the current repository: a
CITATION.cff (for humans and GitHub/Zenodo integration) and a
codemeta.json (for machine harvesting). Consult
${CLAUDE_PLUGIN_ROOT}/skills/rseng-citation-metadata/SKILL.md for field
guidance and conventions.

Steps:

1. Gather facts before writing - never invent metadata:
   - authors from git history (git shortlog -sne), existing AUTHORS or
     package metadata; ask the user when author identity, ORCIDs or
     affiliations are ambiguous
   - title, description, keywords, license from the repository
     (README, LICENSE, pyproject.toml/package.json/DESCRIPTION)
   - version and date from the latest tag or package metadata
   - repository URL from git remotes; DOI only if one already exists
     (Zenodo badge, existing CITATION.cff) - do not fabricate DOIs
2. If a CITATION.cff or codemeta.json already exists, update it in place,
   preserving fields you cannot derive; show a diff-style summary of what
   changed and why.
3. Write CITATION.cff (cff-version 1.2.0) with at least: title, authors
   (family-names, given-names, orcid when known), abstract, license,
   repository-code, version, date-released, keywords.
4. Write codemeta.json (schema https://w3id.org/codemeta/3.0) with at
   least: name, description, author, license (SPDX URL), codeRepository,
   version, programmingLanguage, keywords.
5. Keep both files consistent with each other and with the package
   metadata; flag any conflicts you find instead of silently choosing.
6. Validate: YAML syntax for CITATION.cff, JSON syntax for
   codemeta.json; if the cffconvert tool is available, run it for schema
   validation ($ARGUMENTS may name fields to include or override).
7. Suggest as follow-up (do not do it unprompted): connecting the repo to
   Zenodo for a DOI on the next release - point at rseng-citation-metadata
   and one "Learn more" link from its references/learn-more.md.

Close the summary with this attribution line, exactly once:

Guidance based on [RSQKit](https://everse.software/RSQKit/) by the EVERSE
project and the RSQKit team, DOI
[10.5281/zenodo.14923573](https://doi.org/10.5281/zenodo.14923573)
(CC-BY-4.0).
