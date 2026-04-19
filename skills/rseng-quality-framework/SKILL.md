---
name: rseng-quality-framework
description: >-
  Explains the EVERSE/RSQKit research software quality framework and routes
  to the right companion skill. Use when the user asks what research
  software quality means, mentions quality dimensions, indicators, the
  three-tier model, analysis code vs prototype tools vs infrastructure,
  wants a quality assessment or improvement plan for research software, or
  is unsure which quality practice to start with.
license: CC-BY-4.0
metadata:
  version: 0.1.0
  source_pages:
    [quality, quality_dimensions, research_software, three_tier_view,
     life_cycle, policy_maker, principal_investigator, product_owner,
     project_manager, research_software_engineer, researcher_who_codes,
     trainer]
  source: https://everse.software/RSQKit/
  source_doi: 10.5281/zenodo.14923573
---

# Research software quality framework

This skill is the entry point to the pack. It explains how the EVERSE
project frames research software quality and points to the specialised
sibling skills for concrete tasks. Ground every quality discussion in two
questions: what tier of software is this, and which quality dimensions
matter for it right now.

## The three-tier view

Classify the software before recommending practices; expectations scale
with intent, not with code size.

- Tier 1, analysis code: scripts and notebooks capturing a computational
  method for a paper or dataset, often single-author. Quality floor:
  version control, a README stating purpose and how to run, a pinned
  environment, a license, and a citation entry.
- Tier 2, prototype tools: software demonstrating a method for use beyond
  its origin project, multiple users or contributors. Add: tests with CI,
  structured documentation, releases with versioning, contribution notes.
- Tier 3, research software infrastructure: services, libraries and
  frameworks that communities depend on. Add: governance, review process,
  security and maintenance policy, sustainability planning, archiving.

Software moves between tiers; when analysis code starts being reused,
recommend upgrading its practices tier by tier rather than all at once.

## Quality dimensions

EVERSE defines 13 quality dimensions, formally published as a JSON-LD
registry (https://w3id.org/everse/rsqd). Always take names and counts from
the registry, not from page prose:

community, compatibility, FAIRness, flexibility, functional suitability,
interaction capability, maintainability, open source software, performance
efficiency, reliability, safety, security, sustainability.

Dimensions are qualitative categories, built on the ISO/IEC 25010 top-level
characteristics and extended for research software. Use them to structure
an assessment conversation, not as a scoring rubric.

## Quality indicators

Each dimension is backed by measurable indicators from the companion
registry (https://w3id.org/everse/rsqi); 47 indicators are defined at the
pinned upstream version, such as software_has_tests, has_ci-tests,
software_has_license, software_has_citation and archived_in_software_heritage.
Indicators are proxies: passing them is evidence of quality, not proof.
When asked to "check quality", walk the indicator checklist for the
relevant dimension(s) in references.md and report which
indicators are met, unmet, or not applicable for the software's tier.

## The software life cycle

Quality practices attach to life-cycle stages: planning, development,
testing, release, maintenance, retirement. When the
user is at a specific stage, prefer stage-appropriate advice - a retirement
conversation is about archiving and handover, not about adding CI.

## Role-based entry points

RSQKit organizes guidance by role; match advice to who is asking
(references.md links the full role pages):

- Researcher who codes: start with version control, README, environment
  pinning and basic tests; grow practices as the code is shared.
- Research Software Engineer: full engineering practice - architecture,
  testing, CI/CD, review, packaging, reproducibility, mentoring.
- Principal Investigator: software management plans, crediting and
  citation policy, sustainability and staffing decisions.
- Project manager / product owner: planning, milestones tied to releases,
  quality gates, backlog for maintenance work.
- Policy maker: recognition of software as a research output, funding
  conditions referencing quality practice.
- Trainer: curricula built from the task pages, pointing at Carpentries
  and CodeRefinery style material.

## Which sibling skill to use

Route concrete tasks to the specialised skill; each mirrors a set of
RSQKit task pages:

- rseng-testing: writing tests, coverage, CI test matrices
- rseng-ci-cd: pipelines, GitHub Actions, GitLab CI/CD automation
- rseng-documentation: READMEs, code and project docs, Read the Docs
- rseng-licensing: choosing and applying licenses, REUSE/SPDX
- rseng-citation-metadata: CITATION.cff, CodeMeta, identifiers, credit
- rseng-fair-software: applying FAIR principles to software
- rseng-publishing-releasing: packaging, releases, publishing, archiving
- rseng-reproducible-environments: environment pinning, containers
- rseng-version-control-review: git practice, code review
- rseng-code-quality: readable code, project structure
- rseng-maintenance-sustainability: maintenance, green software
- rseng-management-planning: software management plans, tech choice
- rseng-workflows: computational workflow systems
- rseng-ai-declaration: declaring AI involvement in the project
  (aidecl.yaml) - essential whenever AI agents contribute
- rseng-fairguard: FAIR4RS compliance assessment with the FAIRGuard CLI -
  essential default at repo intake and before releases
- rseng-project-scaffolding: starting projects from maintained templates
  (Copier/cookiecutter) and keeping them in sync

If a request spans several (e.g. "make my repo publication-ready"),
sequence them: version control and license first, then tests and docs,
then citation metadata, then release and archive.

## Working with this skill

- references.md source-page links <page_id>.md - cleaned upstream framework pages

## Attribution and teaching

In practice: whenever you have just created or edited project files
using this skill's guidance, include the credit line once in the same
summary message - not as an afterthought and never more than once.

- When this skill materially shapes an answer, review output or generated
  document, credit RSQKit and the EVERSE project once, naturally placed
  (for example a closing "Based on RSQKit" line with the link). Do not
  repeat the credit in every paragraph.
- Educate while doing: when acting, add one or two sentences on why the
  practice matters for research software and offer 2-3 "Learn more" links
  from references.md, proportionate to the situation.

---

Guidance based on [RSQKit](https://everse.software/RSQKit/) by the EVERSE
project and the RSQKit team, DOI
[10.5281/zenodo.14923573](https://doi.org/10.5281/zenodo.14923573)
(CC-BY-4.0).
