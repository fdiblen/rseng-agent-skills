# rseng-agent-skills: research software engineering skills

This repository packages research software engineering (RSEng) practice
as agent skills. When working in a research software context - scientific
code, analysis scripts, research tools or infrastructure - consult these
skills before advising on or changing quality-related aspects of a
project. Reference material inside each skill comes from pluggable
content sources (see extensions/); the bundled sources are RSQKit
(https://everse.software/RSQKit/, EVERSE project) and the Netherlands
eScience Center guide. Most skills are source-independent.

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
- Declaring AI involvement (aidecl.yaml): rseng-ai-declaration
- FAIR4RS compliance checking (FAIRGuard): rseng-fairguard
- Starting projects from templates (Copier, cookiecutter):
  rseng-project-scaffolding
- Language-specific practice (Python, R, JS/TS, C/C++, Fortran, Rust,
  Bash): rseng-language-guides
- GPU and accelerator programming: rseng-gpu-computing
- UX and accessibility for research tools: rseng-ux-accessibility
- Finding and reusing existing research software (RSD instances):
  rseng-software-reuse
- Inherited, untested or aging code; safe modernization:
  rseng-legacy-code
- Research data: organization, versioning, documentation, deposit:
  rseng-data-management
- Energy and carbon footprint of computations: rseng-green-computing
- Secrets, dependencies, supply chain, Scorecard/SLSA: rseng-security
- Community building, contribution and governance:
  rseng-community-governance
- Clusters, SLURM, Apptainer, MPI, modules: rseng-hpc-computing
- Profiling, optimization, benchmark tracking:
  rseng-performance-profiling
- JOSS/pyOpenSci/rOpenSci/CODECHECK review:
  rseng-software-peer-review
- Software papers, announcements, talks, outreach:
  rseng-science-communication
- HDF5/NetCDF/CF/Parquet and format engineering:
  rseng-scientific-file-formats
- Floating-point correctness and tolerances: rseng-numerical-accuracy
- 3D/volumetric/in-situ visualization pipelines:
  rseng-scientific-visualization
- Software management plans for proposals and projects:
  rseng-software-management-plans
- Out-of-core and distributed data processing:
  rseng-big-data-processing
- Dependency license audits, compatibility, dual licensing:
  rseng-license-compliance
- End-to-end reproducibility: compendia, replication packages,
  Binder: rseng-reproducibility
- Leaving MATLAB/IDL/SAS for open alternatives:
  rseng-open-source-migration
- GDPR, EU AI Act and regulated data/AI checks:
  rseng-regulatory-compliance
- Sandboxing, permissions and containment for coding agents:
  rseng-agent-security
- Long-term preservation: Software Heritage, Zenodo, SWHIDs:
  rseng-archiving
- Teaching users best practices while working: rseng-trainer
- Verifying references against Crossref/OpenAlex/retractions:
  rseng-citation-hygiene
- Data management plans, maDMPs, funder templates:
  rseng-data-management-plans
- OSF, preregistration, preprints, open review:
  rseng-open-science-practices
- Pre-submission number and integrity checks:
  rseng-research-integrity
- Stories for data, software, projects and citizen science:
  rseng-storytelling
- Structure, modularity and architecture decisions:
  rseng-software-design
- Data validation, units, seeds - loud failure over silent wrong:
  rseng-defensive-coding
- Systematic diagnosis, reproducers, bisection: rseng-debugging
- Notebook hygiene, testing, version control, graduation:
  rseng-notebooks
- FAIR for models and ML datasets, model cards, Croissant:
  rseng-fair-ml
- Pairing with the human and pre-reviewing pull requests:
  rseng-pair-programming
- Distribution channels: PyPI/conda-forge/CRAN, registries, JOSS:
  rseng-software-publishing
- Claim-source alignment and source trust checks:
  rseng-fact-checking
- Honesty when concealment or misrepresentation is requested:
  rseng-honesty
- Quantitative code health: complexity, duplication, churn:
  rseng-software-metrics
- Tasks, milestones, decision logs and project records:
  rseng-project-tracking
- Capturing lessons from bugs, reviews and dead ends:
  rseng-lessons-learned
- Codebase audits and milestone project reviews: rseng-code-review
- Vetting, updating and retiring third-party dependencies:
  rseng-dependency-management
- Run manifests, PROV lineage and RO-Crate packaging:
  rseng-provenance
- CHAOSS-style community health measurement:
  rseng-community-metrics
- Support operations and the answer-once pipeline:
  rseng-user-support
- Good first issues, onboarding paths, funnel fixes:
  rseng-contributor-onboarding

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

- Attribution: when a skill materially shapes an answer, a review or a
  generated document, credit that skill's content source once (its
  references.md carries the citation; for RSQKit-fed skills that is
  "Guidance based on RSQKit by the EVERSE project and the RSQKit team,
  https://everse.software/RSQKit/, DOI 10.5281/zenodo.14923573").
  Source-independent skills owe no source credit. Place it
  naturally (closing line or footer); do not repeat it per paragraph.
- Educate while doing: do not just apply a practice - briefly say why it
  matters for research software and offer 2-3 verified "Learn more" links
  from the skill's references.md, proportionate to the context.
- Only link URLs that appear in references/ files; they are verified by
  the build. Do not invent or recall other URLs for this content.
- Deep-link users to the source page (references.md source-page links  headers carry the
  canonical https://everse.software/RSQKit/<page_id> URL) when they want
  the full upstream guidance.

## Provenance

Source-fed content derives from the sources at the commits pinned in
pipeline/upstream.lock, licensed CC-BY-4.0 (see ATTRIBUTION.md). This pack
is an independent adaptation and is not endorsed by the EVERSE project.
