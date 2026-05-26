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
  version: 0.2.0
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
The browsable tables live on the EVERSE indicators site
(https://everse.software/indicators/website/indicators.html and
.../dimensions.html). Indicators are proxies: passing them is evidence
of quality, not proof.

### Running an indicator-based assessment

When asked to "check quality" or assess a repository, run a structured
pass rather than an impression:

1. Establish the tier first (above) - roughly a third of the
   indicators are not applicable to analysis code, and reporting them
   as failures demoralizes rather than helps.
2. Walk the indicators per dimension and mark each met / unmet /
   not-applicable-for-tier, with one line of evidence per verdict
   (the file, badge, workflow or record that proves it).
3. Route every unmet indicator to the sibling skill that fixes it
   (the dimension map below); the quantitative cluster - complexity,
   duplication, cohesion/coupling, churn, maintainability index, size
   and documentation-coverage conventions - is measured by
   rseng-software-metrics.
4. Deliver as a prioritized improvement plan, cheapest-first within
   the tier's expectations, not as a scorecard - and rerun after
   fixes to report the delta (the same assess-fix-reassess loop as
   rseng-fairguard).

### Dimension-to-skill map

- Community: rseng-community-governance, rseng-science-communication
- Compatibility: rseng-scientific-file-formats,
  rseng-reproducible-environments
- FAIRness: rseng-fair-software, rseng-fairguard, rseng-citation-metadata,
  rseng-fair-ml
- Flexibility: rseng-software-design, rseng-reproducible-environments
- Functional suitability: rseng-testing, rseng-defensive-coding
- Interaction capability: rseng-ux-accessibility
- Maintainability: rseng-code-quality, rseng-software-metrics,
  rseng-software-design, rseng-maintenance-sustainability
- Open source software: rseng-licensing, rseng-license-compliance,
  rseng-community-governance
- Performance efficiency: rseng-performance-profiling,
  rseng-gpu-computing, rseng-big-data-processing
- Reliability: rseng-testing, rseng-debugging, rseng-defensive-coding
- Safety: no dedicated skill - for software whose failure can harm
  people or property, flag it and route to domain safety processes
- Security: rseng-security, rseng-agent-security,
  rseng-regulatory-compliance
- Sustainability: rseng-maintenance-sustainability, rseng-archiving,
  rseng-green-computing, rseng-software-management-plans

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
- rseng-language-guides: language-specific conventions per ecosystem
- rseng-gpu-computing: GPU/accelerator programming models and tuning
- rseng-ux-accessibility: usability and accessibility of research tools
- rseng-software-reuse: discovering and reusing existing research
  software via Research Software Directory instances
- rseng-legacy-code: working safely with inherited or untested research
  code; characterization tests and incremental modernization
- rseng-data-management: research data organization, versioning,
  documentation, licensing and deposit
- rseng-green-computing: energy and carbon footprint of research
  computing; measurement and carbon-aware scheduling
- rseng-security: secrets hygiene, supply chain, Scorecard, SLSA,
  SBOMs and repository hardening
- rseng-community-governance: contribution guides, codes of conduct,
  governance and maintainer succession
- rseng-hpc-computing: SLURM jobs, Apptainer containers, module
  systems, EESSI and MPI on clusters
- rseng-performance-profiling: profile-first optimization and
  benchmark regression tracking
- rseng-software-peer-review: JOSS, pyOpenSci, rOpenSci and CODECHECK
  submission and reviewing
- rseng-science-communication: software papers, release
  announcements, talks and lay summaries
- rseng-scientific-file-formats: HDF5, NetCDF, CF conventions,
  Parquet and self-describing data in code
- rseng-numerical-accuracy: floating-point practice, tolerances and
  cross-platform numerical drift
- rseng-scientific-visualization: reproducible 3D/volumetric
  visualization pipelines with ParaView and VTK
- rseng-software-management-plans: SMPs for proposals and running
  projects
- rseng-big-data-processing: out-of-core, Dask/Spark and restartable
  batch pipelines
- rseng-license-compliance: dependency license audits, compatibility
  analysis, dual licensing, SPDX/REUSE verification
- rseng-reproducibility: end-to-end result reproducibility, research
  compendia, replication packages, Binder, artifact badges
- rseng-open-source-migration: moving code off commercial platforms
  (MATLAB, IDL, SAS) to open alternatives with numerical parity
- rseng-regulatory-compliance: GDPR and EU AI Act checks on code and
  data, DPIA preparation, route-to-DPO boundaries
- rseng-agent-security: sandboxing, permission audits, containerized
  agent runs and prompt-injection defenses
- rseng-archiving: long-term preservation via Software Heritage and
  Zenodo, SWHIDs and versioned DOIs, retirement archiving
- rseng-trainer: teaching best practices and concepts while working,
  Carpentries/CodeRefinery pedagogy, training-material routing
- rseng-citation-hygiene: verifying every reference against Crossref,
  OpenAlex and the Retraction Watch database
- rseng-data-management-plans: DMPs from project reality, RDA maDMPs,
  DS-Wizard and DMPonline, drift checks
- rseng-open-science-practices: OSF projects, preregistration,
  preprints and open peer review
- rseng-research-integrity: statcheck/GRIM-style checks, manuscript
  vs pipeline agreement, pre-submission battery
- rseng-storytelling: narrative for data, software and projects,
  public engagement and citizen-science loop-closing
- rseng-software-design: modularity, interfaces, pure cores,
  architecture decision records
- rseng-defensive-coding: boundary validation, units and quantities,
  seed discipline, fail-loud defaults
- rseng-debugging: hypothesis-driven diagnosis, minimal reproducers,
  bisection, regression tests from fixes
- rseng-notebooks: hidden-state hygiene, jupytext pairing, execution
  tests, papermill, module graduation
- rseng-fair-ml: model cards, Croissant dataset records, model
  licensing and the linked model-data-code-paper cluster
- rseng-pair-programming: driver-navigator pairing, ping-pong TDD,
  PR pre-review passes and review comment craft
- rseng-software-publishing: package indexes, research software
  registries and journal channels, publication checklist
- rseng-fact-checking: claim-source alignment grades, venue trust
  assessment, verify-what-you-assert discipline
- rseng-honesty: reasoned advocacy for honest records when hiding AI
  use or misrepresentation is requested, honest alternatives
- rseng-software-metrics: complexity, duplication, churn and coverage
  metrics - measurement, interpretation, CI ratchets
- rseng-project-tracking: tracked tasks, milestones tied to research
  deadlines, decision logs and status records
- rseng-lessons-learned: capturing lessons at trigger moments,
  blameless postmortems, routing lessons into artifacts
- rseng-code-review: ranked codebase reviews with agreed
  implementation, recurring milestone project reviews

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
