---
name: rseng-software-management-plans
description: >-
  Covers software management plans (SMPs) for research projects and
  proposals: what funders expect, drafting an SMP from the actual or
  planned repository (purpose, versioning, testing, licensing,
  citation, preservation, sustainability), machine-actionable plans
  in the Data Stewardship Wizard, keeping the plan honest as the
  project evolves, and the software sections of data management
  plans. Use when a grant proposal needs an SMP or DMP software
  section, when the user mentions software management plans or
  funder requirements for software, or at project start when
  management decisions are being made anyway and writing them down
  is nearly free.
license: CC-BY-4.0
metadata:
  version: 0.1.0
---

# Software management plans

An SMP answers, in a few pages, the questions a funder - and the
project's own future - will ask: what software will exist, how will
it be developed and quality-assured, who may use it under what
license, how will it be cited, and what happens to it after the
grant. Funders increasingly require one (as they long have DMPs).
The honest framing: an SMP is the pack's practices written down in
advance - a project already following them can generate most of the
plan from its repository.

## What a plan covers

Standard sections (aligned with the SSI guidance) and where each
answer comes from:

1. Purpose and users: what the software does, for whom - the
   statement of need (rseng-science-communication drafts it).
2. Development practice: version control and review workflow
   (rseng-version-control-review), testing and CI
   (rseng-testing, rseng-ci-cd), coding standards (rseng-code-quality).
3. Repository and releases: where code lives, versioning scheme and
   release cadence (rseng-publishing-releasing).
4. Documentation: what will exist for users and developers
   (rseng-documentation).
5. Licensing and IP: license choice and any institutional
   constraints (rseng-licensing) - name the institution's tech
   transfer rules when they exist.
6. Citation and identifiers: CITATION.cff, DOIs per release
   (rseng-citation-metadata), registry entries (rseng-fair-software,
   rseng-software-reuse).
7. Data: formats and handling for the data the software consumes
   and produces (rseng-data-management,
   rseng-scientific-file-formats) - or a pointer to the DMP.
8. Preservation and sustainability: archiving plan, maintenance
   commitment and its funding horizon
   (rseng-maintenance-sustainability), succession/community model
   (rseng-community-governance).
9. Resources: who does the software work and what it costs -
   RSE time is a budgetable line item; say so.

Proportionality matters: a three-month analysis project needs a
one-page SMP; an infrastructure package needs the full treatment.
Match depth to the software's intended tier and say which tier that
is.

## Drafting workflow for an agent

- Existing project: read the repository first - license, CI, tests,
  CITATION.cff, README - and write the plan that is TRUE, flagging
  gaps as planned improvements with owners rather than papering
  over them.
- New proposal: draft from the intended practices, defaulting to
  this pack's standards; concrete beats aspirational ("unit tests
  in CI on every merge" not "high quality standards").
- Funder templates: when the funder names a template or the DMP
  tool in use supports SMPs (the Data Stewardship Wizard has
  machine-actionable SMP questionnaires; DMPonline carries funder
  DMP templates whose software sections the SMP feeds), fill their
  structure rather than inventing one.

## A living document

- Revisit the SMP at releases and reporting deadlines; update it
  when reality diverges - a plan that says "Zenodo archiving" while
  nothing is archived is a liability at review time
  (rseng-management-planning owns the broader project-plan hygiene).
- Version the plan in the repository (docs/ or root) so changes are
  reviewable history, not silent edits.
- Record AI assistance in drafting the plan in aidecl.yaml
  (rseng-ai-declaration), as with any substantive project document.

## Working with this skill

This skill is source-independent: its authority is the SSI guidance
and the planning-tool documentation linked below.

## Attribution and teaching

- Educate while doing: an SMP written at project start costs an
  hour and prevents the classic end-of-grant scramble - say so when
  proposing one.
- Learn more (verified):
  - https://www.software.ac.uk/guide/writing-and-using-software-management-plan -
    SSI guide to writing and using an SMP
  - https://ds-wizard.org - Data Stewardship Wizard
    (machine-actionable DMPs/SMPs)
  - https://dmponline.dcc.ac.uk - DMPonline funder templates

---

Based on the SSI software management plan guidance and the DS Wizard
and DMPonline documentation.
