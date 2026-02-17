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
     life_cycle]
  source: https://everse.software/RSQKit/
  source_doi: 10.5281/zenodo.14923573
---

# Research software quality framework

This skill is the entry point to the pack. It explains how the EVERSE
project frames research software quality and points to the specialised
sibling skills for concrete tasks. Ground every quality discussion in two
questions: what tier of software is this, and which quality dimensions
matter for it right now (RSQKit: quality).

## The three-tier view

Classify the software before recommending practices; expectations scale
with intent, not with code size (RSQKit: three_tier_view).

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
the registry, not from page prose (RSQKit: quality_dimensions):

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
relevant dimension(s) in references/indicators.md and report which
indicators are met, unmet, or not applicable for the software's tier.

## The software life cycle

Quality practices attach to life-cycle stages: planning, development,
testing, release, maintenance, retirement (RSQKit: life_cycle). When the
user is at a specific stage, prefer stage-appropriate advice - a retirement
conversation is about archiving and handover, not about adding CI.

## Working with this skill

- references/pages/<page_id>.md - cleaned upstream framework pages
- references/indicators.md - the full dimension/indicator checklist
- references/learn-more.md - verified external pointers

## Attribution and teaching

- When this skill materially shapes an answer, review output or generated
  document, credit RSQKit and the EVERSE project once, naturally placed
  (for example a closing "Based on RSQKit" line with the link). Do not
  repeat the credit in every paragraph.
- Educate while doing: when acting, add one or two sentences on why the
  practice matters for research software and offer 2-3 "Learn more" links
  from references/learn-more.md, proportionate to the situation.

---

Guidance based on [RSQKit](https://everse.software/RSQKit/) by the EVERSE
project and the RSQKit team, DOI
[10.5281/zenodo.14923573](https://doi.org/10.5281/zenodo.14923573)
(CC-BY-4.0).
