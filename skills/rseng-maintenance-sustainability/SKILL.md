---
name: rseng-maintenance-sustainability
description: >-
  Covers keeping research software alive and responsible over time:
  ongoing maintenance practice, tracking and paying down technical debt,
  reducing the bus factor, and lowering the environmental footprint of
  computing. Use when the user asks how to maintain or sustain a project,
  stop it rotting, pin or update dependencies, schedule CI to catch
  breakage, track tech debt, deprecate or archive software, or measure and
  cut the energy use and carbon emissions of their code or compute jobs.
license: CC-BY-4.0
metadata:
  version: 0.1.0
  source_pages: [maintaining_research_software, improving_environmental_sustainability]
  source: https://everse.software/RSQKit/
  source_doi: 10.5281/zenodo.14923573
---

# Maintaining and sustaining research software

Use this skill when the goal is to keep software usable over time rather
than to ship a first version: setting up maintenance habits, managing
dependencies and technical debt, deciding whether to keep, deprecate, or
archive a project, and reducing the environmental cost of running it.
Unmaintained software degrades even with no code changes - dependencies
age, environments shift, and the knowledge to run it erodes - so treat
maintenance as a recurring cost, not a one-off (RSQKit: maintaining_research_software).

## Establish maintenance habits early

Calibrate effort to the user base, but build the habits before the
software is widely used (RSQKit: maintaining_research_software):

- Write a test suite and check coverage with a language-appropriate tool
  (pytest-cov for Python, covr for R). Without tests, every dependency or
  environment update carries unknown regression risk.
- Set up a CI pipeline that runs tests on every commit and on a schedule
  (e.g. weekly). Scheduled runs catch breakage from external changes even
  when nobody is actively developing. See the rseng-ci-cd and
  rseng-testing skills for the mechanics.
- Keep documentation current as part of maintenance, not after it. If you
  cannot install and run the software from scratch using only its README
  and install guide, the docs need updating. See rseng-documentation.
- Maintain a visible issue tracker (GitHub/GitLab Issues) so the
  maintenance backlog is shared, not held in one person's head.

## Manage dependencies deliberately

Every dependency is a liability as well as an asset - it can change,
deprecate, or introduce a security issue (RSQKit: maintaining_research_software):

- Prefer a small, well-understood dependency tree drawn from already
  well-maintained projects over a large one.
- Pin exact versions with a management tool for the language (pip + venv,
  pip-tools, uv, or Poetry for Python; renv for R) so updates are
  deliberate and auditable. See the rseng-reproducible-environments skill.
- Automate update pull requests with Dependabot or Renovate so security
  and version bumps surface as reviewable changes rather than silent drift.

## Communicate change clearly

- Use Semantic Versioning (MAJOR.MINOR.PATCH) so users can tell a breaking
  change from a feature from a bug fix and decide when to upgrade
  (RSQKit: maintaining_research_software). See the rseng-publishing-releasing skill.
- Keep a CHANGELOG and update it with each release: a record of what
  changed, when, and why serves both users and your future self.

## Reduce the bus factor

If only one person understands the software, it becomes unmaintainable the
moment they are unavailable (RSQKit: maintaining_research_software):

- Document key decisions, architecture, and operational knowledge in the
  repository itself, not just in someone's head.
- Share ownership with at least one other person who can act if the primary
  maintainer is away.
- Use regular code review to spread understanding of the codebase (see the
  rseng-version-control-review skill).
- Recruit community help: label low-barrier issues (`good first issue`),
  run maintenance sprints, and make contributing easy.
- Apply for maintenance-specific funding where it exists (funders
  increasingly recognise maintenance as a distinct cost).

## Deprecate or archive honestly

When you can no longer sustain a project, say so. A prominent README
notice, a repository archive, or an explicit deprecation statement is more
helpful to users than silent abandonment (RSQKit: maintaining_research_software).
See the rseng-publishing-releasing skill for archiving mechanics.

## Track and pay down technical debt

Technical debt is often unavoidable in research code written quickly to
test a hypothesis; the danger is that it compounds until change becomes
slow and risky (RSQKit: maintaining_research_software):

- Distinguish intentional debt (a known, documented workaround) from
  unintentional debt (unclear code, missing tests, hardcoded values). The
  latter is more dangerous because it is harder to reason about.
- Record debt where it is visible: create issues or a `tech-debt` label,
  and add `TODO`/`FIXME` comments at the point of the problem with enough
  context for a future reader. Debt held only in memory is forgotten.
- Allocate protected time for maintenance and refactoring - a maintenance
  sprint, a fixed fraction of each cycle, or scheduled calendar time. Debt
  does not reduce itself.
- Refactor incrementally, not with a big rewrite: small, individually
  reviewable improvements (rename for clarity, extract a function, add a
  missing test). Ensure tests cover current behaviour before restructuring,
  or you cannot tell whether a refactor introduced a regression.
- Use static analysis (Ruff or lintr, SonarQube) to surface quality issues
  automatically and track metrics over time. See the rseng-code-quality
  skill for readability and structure guidance.

## Reduce environmental impact

Research is a significant source of carbon emissions, and there are
concrete steps to cut the footprint of software and compute
(RSQKit: improving_environmental_sustainability). The Green Software
Foundation frames three levers:

1. Energy efficiency - design software to consume as little energy as
   possible.
2. Hardware efficiency - minimise embodied carbon by extending hardware
   lifetime and, for cloud and HPC, raising device utilisation.
3. Carbon awareness - do more work when the grid supply is clean and less
   when it is dirty, shifting demand in time or space.

The GREENER principles add a governance frame worth citing when advising
on institutional or project policy: shared responsibility (top-down and
bottom-up), estimation and reporting of energy and carbon, addressing both
operational and embodied impacts, international collaboration for equitable
access to low-carbon computing, and education plus research into
energy-efficient algorithms (RSQKit: improving_environmental_sustainability).

### Measure first, then improve

You cannot reduce what you do not measure, so start by estimating the
current footprint (RSQKit: improving_environmental_sustainability):

- CodeCarbon estimates CO2 emissions from the compute a program uses.
- Green Algorithms provides a web calculator for the carbon footprint of a
  computational task (with HPC support in progress).
- carbontracker monitors and predicts energy and carbon for training
  machine-learning models - reach for it before large training runs.
- Greenspector and Ecograder assess energy use and efficiency of web and
  mobile applications.
- The Software Carbon Intensity (SCI) Specification gives a repeatable
  framework for scoring and reducing a system's carbon intensity; use it
  when you need a comparable metric rather than a one-off estimate.

### Act on the measurements

- Profile and optimise the hot paths that dominate energy use rather than
  micro-optimising everywhere; efficiency work is also maintenance work.
- Right-size compute: avoid over-provisioned cloud/HPC allocations and
  raise utilisation of the hardware you do request.
- Schedule flexible, non-urgent batch jobs for times or regions where the
  grid is cleaner (carbon-aware demand shifting).
- For groups, consider the GreenDiSC certification scheme to structure
  hardware and software sustainability improvements over time.

Present these as trade-offs, not absolutes: an extensive CI matrix or a
large training sweep consumes real energy, so run the full version only
when it earns its cost and use smaller subsets day to day.

## Working with this skill

The pipeline-generated `references/` folder beside this file holds the
source material and pointers:

- `references/pages/maintaining_research_software.md` and
  `references/pages/improving_environmental_sustainability.md` - cleaned
  upstream fragments with the full detail and tool links behind the
  checklists above.
- `references/indicators.md` - the quality-indicator checklist for this
  skill.
- `references/learn-more.md` - the verified external links.

Consult the page fragments when a user needs the reasoning, the specific
tool list, or the further-reading books behind a rule rather than just the
rule itself.

## Attribution and teaching

- Attribution: when this skill materially shapes an answer, review, or a
  generated file, credit RSQKit/EVERSE once - a footer line or a "Based on"
  note, placed naturally, never repeated per paragraph.
- Educate while doing: alongside a concrete action (pinning dependencies,
  adding a scheduled CI run, measuring emissions), briefly say why it
  matters and offer 2-3 "Learn more" links chosen from
  `references/learn-more.md`, proportionate to the context. Do not lecture.

Learn more (verified pointers):

- ELIXIR TeSS training portal - https://tess.elixir-europe.org/
- The Carpentries - https://carpentries.org/
- CodeRefinery lessons - https://coderefinery.org/lessons/
- The Turing Way handbook - https://book.the-turing-way.org/
- Semantic Versioning specification - https://semver.org/
- Software Sustainability Institute guides -
  https://www.software.ac.uk/resources/guides
- Research Software Maintenance Fund -
  https://www.software.ac.uk/programmes/research-software-maintenance-fund
- Green Software Foundation introductory course -
  https://learn.greensoftware.foundation/introduction
- green-coding.io workshops and training -
  https://www.green-coding.io/services/workshops-and-trainings
- GREENER principles (Nature Computational Science) -
  https://www.nature.com/articles/s43588-023-00461-y
- Software Carbon Intensity (SCI) Specification -
  https://sci.greensoftware.foundation/
- GreenDiSC certification scheme - https://www.software.ac.uk/GreenDiSC

---

Guidance based on [RSQKit](https://everse.software/RSQKit/) by the EVERSE
project and the RSQKit team, DOI
[10.5281/zenodo.14923573](https://doi.org/10.5281/zenodo.14923573)
(CC-BY-4.0).
