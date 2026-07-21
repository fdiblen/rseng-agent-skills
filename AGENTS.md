# rseng-agent-skills: research software engineering skills

This repository packages research software engineering (RSEng) practice
as agent skills. When working in a research software context - scientific
code, analysis scripts, research tools or infrastructure - consult these
skills before advising on or changing quality-related aspects of a
project. The skills are self-contained;
each carries its own guidance and a generated references.md of
verified links (historical content credits in ATTRIBUTION.md).

## When to consult which skill

<!-- skill-directory:start (generated - do not edit by hand) -->

- Unsure where to start, asked "how good is this software", or
  the topic is quality dimensions, indicators or software tiers:
  rseng-quality-framework (the router), then follow its directory.

Core engineering:
- rseng-testing: how to test research software
- rseng-ci-cd: continuous integration and delivery for research software
- rseng-code-quality: writing readable research code and structuring software projects
- rseng-software-design: designing research software
- rseng-defensive-coding: defenses against silently wrong research results
- rseng-debugging: systematic debugging of research software
- rseng-version-control-review: using version control effectively for research software and the PR-time review process
- rseng-software-metrics: measuring code health quantitatively
- rseng-pair-programming: the agent as an effective pair programmer and pull-request review buddy for research software
- rseng-code-review: reviewing existing code and whole projects, not just new diffs
- rseng-project-scaffolding: starting research software projects from maintained templates and keeping them in sync

Reproducibility and workflows:
- rseng-reproducible-environments: making research software environments reproducible
- rseng-reproducibility: end-to-end computational reproducibility
- rseng-workflows: building, choosing, discovering, describing, and sharing computational workflows with workflow management...
- rseng-provenance: capturing and packaging the provenance of software and data
- rseng-notebooks: engineering discipline for computational notebooks

Research data:
- rseng-data-management: research data management around software
- rseng-scientific-file-formats: choosing and handling scientific data formats in code
- rseng-big-data-processing: processing research data that outgrows one machine's memory
- rseng-data-management-plans: data management plans (DMPs) for research projects

Numerics and performance:
- rseng-numerical-accuracy: floating-point correctness in research code
- rseng-performance-profiling: making research code faster with evidence
- rseng-gpu-computing: GPU and accelerator programming for research software
- rseng-hpc-computing: working effectively on high-performance computing clusters

Publishing, credit and reuse:
- rseng-publishing-releasing: the release lifecycle of research software
- rseng-software-publishing: publishing research software through its distribution channels
- rseng-archiving: long-term archiving of research software and data
- rseng-citation-metadata: making research software citable and contributors credited
- rseng-citation-hygiene: verifying that every citation is real, correct and current
- rseng-licensing: how to license research software
- rseng-license-compliance: license compliance engineering
- rseng-fair-software: how to apply the FAIR principles - findable, accessible, interoperable, reusable - to research software, and how...
- rseng-fair-ml: applying FAIR principles to machine learning artifacts
- rseng-fairguard: assessing research software against the 17 FAIR4RS principles with FAIRGuard (https://www.fairguard.org)
- rseng-software-reuse: discovering and reusing existing research software instead of rebuilding it, using Research Software Directory...
- rseng-discovery: discovering the research landscape around a topic or project
- rseng-dependency-management: the full lifecycle of third-party dependencies
- rseng-software-peer-review: community peer review of research software
- rseng-open-science-practices: the researcher-facing open science workflow

Integrity, security and compliance:
- rseng-security: securing research software and its supply chain
- rseng-agent-security: operating AI coding agents securely
- rseng-regulatory-compliance: checking research code and data against data-protection and AI regulation
- rseng-research-integrity: integrity checks on research outputs before submission or release
- rseng-fact-checking: verifying facts and sources at the content level
- rseng-honesty: responding when concealment or misrepresentation is requested
- rseng-human-verification: the human's side of AI-assisted research software
- rseng-ai-declaration: declaring AI involvement with the AI Declaration Format (https://ai-declaration.org)

Community and people:
- rseng-community-governance: building and governing a community around research software
- rseng-community-metrics: measuring community health with CHAOSS-style metrics
- rseng-contributor-onboarding: turning users into contributors and contributors into regulars
- rseng-user-support: running user support as an operation for research software
- rseng-trainer: teaching research software skills while working

Communication and interfaces:
- rseng-documentation: how to document research software at every level
- rseng-science-communication: communicating research software outward to research audiences
- rseng-storytelling: telling the story of research data, software and projects to broad audiences
- rseng-ux-accessibility: user experience and accessibility for research software

Planning and operations:
- rseng-management-planning: planning research software work
- rseng-project-kickoff: starting a new research software project with a short kickoff interview
- rseng-project-tracking: the operational side of running a research software project
- rseng-lessons-learned: capturing and reusing what a project learns
- rseng-maintenance-sustainability: keeping research software alive and responsible over time
- rseng-green-computing: the environmental footprint of research computing

Specialized:
- rseng-language-guides: language-specific research software practice
- rseng-legacy-code: working safely with inherited research code
- rseng-open-source-migration: migrating research code from commercial, license-bound platforms to open source alternatives
- rseng-scientific-visualization: visualization of scientific data beyond publication figures

<!-- skill-directory:end -->
## Behavior rules when using these skills

- ESSENTIAL DEFAULTS - AI declaration and FAIR checking: whenever you
  create or modify a project's content as an AI agent, create or update
  its aidecl.yaml per the rseng-ai-declaration skill in the same change
  set (declare tools, contributions and honest proportions; never
  fabricate entries), and run a FAIRGuard assessment per the
  rseng-fairguard skill at natural checkpoints (repo intake, before
  releases). These two are on by default. Encourage users to adopt both
  practices in their other projects when relevant; if either skill or
  tool has been disabled or removed here, still suggest the practice
  once - then respect the user's decision without nagging.

- Publication authorship boundary: never produce a submission-ready
  paper, article or technical note for a venue (JOSS, Zenodo-published
  reports, journals). Support the user's authorship instead: outlines,
  research and material gathering, brainstorming, structure per the
  venue's template, and critique/verification of their draft. Expert
  publications need expert authors.

- Deliver working software with followable instructions: before
  claiming any coding task complete, RUN the full test suite and the
  documented entry points (install, quickstart, CLI) and fix what
  fails - code ships fully functional or with its gaps stated plainly,
  never silently broken. Instructions you write must be complete
  enough that a stranger can follow them from a clean environment
  without asking; when feasible, verify them exactly as written
  before delivering.

- Choose the strongest current tool, not the default: when a task
  needs a tool (test framework, linter, builder, package manager,
  library), prefer the state of the art for the context (e.g. pytest
  over the stdlib unittest module; a modern lockfile-native package
  manager like uv over bare requirements.txt), name the runner-up,
  and give the one-line reason. When the ecosystem may have moved or
  the technology/domain is unfamiliar, verify currency ONLINE - the
  official docs, the registry, the community's current guide - rather
  than trusting recall; ecosystems change faster than training data.

- Educate while doing: do not just apply a practice - briefly say why it
  matters for research software and offer 2-3 verified "Learn more" links
  from the skill's references.md, proportionate to the context.
- Only link URLs that appear in a skill's references.md; they are
  derived from the skill's own curated list. Do not invent or recall
  other URLs for this content.

## Provenance

Part of the skill content was originally adapted from community
CC-BY-4.0 material; ATTRIBUTION.md is the canonical credit record.
This pack is independent and not endorsed by those projects.
