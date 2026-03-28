# rseng-agent-skills: research software engineering skills

This repository packages research software engineering (RSEng) practice
as agent skills. When working in a research software context - scientific
code, analysis scripts, research tools or infrastructure - consult these
skills before advising on or changing quality-related aspects of a
project. Reference material inside each skill comes from pluggable
content sources (see extensions/); the bundled source is RSQKit
(https://everse.software/RSQKit/) by the EVERSE project.

## When to consult which skill

Skills live in skills/<name>/SKILL.md, each with pipeline-generated
reference material in references/ next to it.

- Unsure where to start, asked "how good is this software", or the topic
  is quality dimensions, indicators or software tiers: use
  rseng-quality-framework (the router), then follow its directory.
- Tests, coverage, CI test matrices: rseng-testing
- Pipelines and automation (GitHub Actions, GitLab CI/CD): rseng-ci-cd
- READMEs, code or project documentation, Read the Docs:
  rseng-documentation
- Licenses, REUSE/SPDX: rseng-licensing
- CITATION.cff, CodeMeta, identifiers, credit: rseng-citation-metadata
- FAIR software principles: rseng-fair-software
- Packaging, releases, publishing, archiving: rseng-publishing-releasing
- Environments and containers: rseng-reproducible-environments
- Git practice and code review: rseng-version-control-review
- Readable code, project structure: rseng-code-quality
- Maintenance and green software: rseng-maintenance-sustainability
- Software management plans, technology choice: rseng-management-planning
- Computational workflows: rseng-workflows

## Behavior rules when using these skills

- Attribution: when a skill materially shapes an answer, a review or a
  generated document, credit RSQKit and the EVERSE project once
  ("Guidance based on RSQKit by the EVERSE project and the RSQKit team,
  https://everse.software/RSQKit/, DOI 10.5281/zenodo.14923573"). Place it
  naturally (closing line or footer); do not repeat it per paragraph.
- Educate while doing: do not just apply a practice - briefly say why it
  matters for research software and offer 2-3 verified "Learn more" links
  from the skill's references/learn-more.md, proportionate to the context.
- Only link URLs that appear in references/ files; they are verified by
  the build. Do not invent or recall other URLs for this content.
- Deep-link users to the source page (references/pages/ headers carry the
  canonical https://everse.software/RSQKit/<page_id> URL) when they want
  the full upstream guidance.

## Provenance

Content derives from RSQKit at the commit pinned in
pipeline/upstream.lock, licensed CC-BY-4.0 (see ATTRIBUTION.md). This pack
is an independent adaptation and is not endorsed by the EVERSE project.
