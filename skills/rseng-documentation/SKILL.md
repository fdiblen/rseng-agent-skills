---
name: rseng-documentation
description: >-
  Covers how to document research software at every level: writing a
  README, code-level docs (comments, docstrings, API and CLI help),
  project docs (INSTALL, CONTRIBUTING, LICENSE, CITATION, changelog),
  publishing hosted documentation with Read the Docs, and capturing a
  Research Software Story. Use when the user asks how to write or improve
  a README, add docstrings or inline comments, document an API or CLI,
  set up Sphinx/MkDocs/Doxygen, host docs on Read the Docs, structure a
  docs site, or write the narrative context and history behind a project.
license: CC-BY-4.0
metadata:
  version: 0.1.0
  source_pages: [software_documentation, documenting_code, documenting_software_project, documenting_software_readthedocs, creating_good_readme, writing_research_software_story]
  source: https://everse.software/RSQKit/
  source_doi: 10.5281/zenodo.14923573
---

# Documenting research software

Use this skill when creating or improving any documentation for research
software: a README, in-code comments and docstrings, API/CLI references,
project files like CONTRIBUTING or CHANGELOG, a hosted documentation site,
or a narrative Research Software Story. Good documentation makes software
understandable, reusable, and sustainable - it tells others (and your
future self) what the software does, how to use it, and how to contribute.

## Separate the two levels first

Decide which level the user needs before writing, because audience and
content differ:

- Project documentation - the software as a whole: purpose, audience,
  installation, usage, licensing, contribution. Lives in README, INSTALL,
  CONTRIBUTING, LICENSE, CITATION. Helps people use and adopt the software.
- Code documentation - how the code works internally: comments, docstrings,
  architecture notes, API references. Helps people develop, deploy, and
  sustain it.

Both matter; keep them consistent. Installation and usage often straddle
the line and serve users and developers alike, so link between the two
rather than duplicating.

Cross-cutting rules for all documentation:

- Keep it accessible, clear, consistent, and regularly updated; cover all
  key aspects and invite feedback. Outdated docs can be worse than none.
- Generate it automatically where possible and use standard formats:
  Markdown, reStructuredText, HTML, PDF, or a wiki.
- Store documentation in the repository and version-control it alongside
  the code so it moves through the same review workflow.

## Write a good README

The README is the entry point and the project's homepage on GitHub or
GitLab. Place it in the project root as plain text or Markdown so it ships
with the code. Aim for three qualities: understandability, usability, and
attribution.

Include these sections, adapting depth to the audience:

- Description - purpose and features of the software.
- Requirements - software and hardware needs (OS, interpreter version,
  extra services, infrastructure). Skip low-level library dependencies;
  express those through the language's own mechanism (e.g. requirements.txt).
- Installation - exhaustive, copy-pasteable commands assuming no prior
  knowledge; cover multiple install paths (library, Docker, script) if they
  exist, and link out for heavyweight prerequisites.
- Configuration - config-file fields and how to set them, when needed.
- Usage - every parameter/subcommand with worked examples; link to tutorials
  in other formats (video, notebook, PDF).
- Contribution - how to propose changes (pull requests, issues, standards).
- Acknowledgements - funders and contributors, per each institution's policy.
- Citation - how to cite, ideally mirroring a CITATION.cff file (e.g. BibTeX).
- License - state it explicitly; unlicensed software cannot legally be reused.

For research software also document how to reproduce or replicate the
experiments, add citation information, and describe links to related
publications and datasets.

Extra tactics: add badges for at-a-glance status (see the howfairis list);
run SOMEF to detect missing README parts (it flags gaps, it does not grade).
If AI assists in drafting a README, hold it to the same accuracy bar -
verify every command, requirement, and citation before publishing.

## Document the code

Match documentation type to purpose and audience - user, developer, and
deployment documentation each target different readers, so tailor content
accordingly; personas help.

Document as you code:

- Comments live in the source for people modifying the code; docstrings are
  visible to the outside world for people using it. Use both.
- Write comments and docstrings while coding so they stay current. Explain
  *why* and *how*, not a restatement of *what*. If code needs heavy
  commenting to be understood, rewrite the code instead.
- Lean on IDEs and extensions (autoDocstring, JSDoc) to scaffold docstrings.

Write meaningful error messages that state when and where the error
happened, what went wrong, the software state, and how to fix it or where
to look.

Include usage examples, a quickstart for a fast path to experimentation,
and a fuller step-by-step tutorial. Move examples to a dedicated section if
they clutter the main docs.

Document any CLI or API: describe usage, subcommands, options, arguments,
and environment variables with examples. Implement a `help` command so users
succeed without external docs. Tools: Click for Python CLIs, the OpenAPI
Specification and Swagger for REST APIs.

Automate generation from annotated source where you can:

- Sphinx (Python and more), Doxygen (C++ and more), Roxygen (R), JSDoc
  (JavaScript), Documenter.jl (Julia) extract docs from code comments into
  HTML/PDF.
- MkDocs builds Markdown documentation sites.
- Wire doc builds into CI (GitHub Actions, GitLab CI/CD) to publish updates
  automatically; Zenodo can archive docs with each release.

## Document the software project

Beyond the README, a well-documented project provides these root-level
files or clearly linked pointers:

- INSTALL - download and run steps (or a README section).
- LICENSE - legal conditions for use (see the licensing skill).
- CITATION - a CFF or text file stating how to cite (see the citation skill).
- CONTRIBUTING - how to get involved and submit changes.
- CODE_OF_CONDUCT - the collaboration norms for the community.
- AUTHORS/CONTRIBUTORS - who built it, inline or in a separate file.
- Pointers to deeper technical docs (API, deployment, architecture).
- Roadmap - current and planned work, or a link to the issue tracker.
- Changelog / release notes - notable changes between versions.

Organize it for the reader: identify the audience, state the purpose,
structure information logically, keep it current, make it easy to find and
navigate (e.g. GitHub Pages), and include enough detail - environment,
data, example workflows - for others to reproduce results.

## Publish hosted documentation with Read the Docs

When a project needs a browsable docs site, generate static pages with
Sphinx or MkDocs and publish them. Read the Docs is a common host that
integrates with GitHub/GitLab and rebuilds via CI:

1. Create the source: `sphinx-quickstart` (Sphinx) or `mkdocs new my-project`
   (MkDocs).
2. Push code and docs to a Git remote on GitHub or GitLab.
3. Import the project on Read the Docs: link the account, pick the repo, set
   name, doc type, branch, and any Python requirements.
4. Add a `.readthedocs.yaml` (config version 2) at the repo root declaring
   the Python environment and the builder (`sphinx: configuration: ...` or
   `mkdocs: config: ...`).
5. Set up webhooks / CI so pushes and pull requests trigger rebuilds.
6. Customise theme and add PDF/ePub outputs if needed; check build logs.
7. Publish - docs appear at `https://<your-project>.readthedocs.io/`.

## Write a Research Software Story

A Research Software Story captures the context around a project rather than
how to run it: the scientific problem, the community, and the practices and
tools that sustain it - the who, what, why, where, when, and how. It helps
onboard newcomers, explains the project to leaders and funders, and, through
the act of writing, surfaces gaps the team had not noticed.

Guide the user through the template sections - the problem addressed, the
communities involved, the technical nature, dependencies, development
practices, onboarding, tooling, documentation/FAIR/openness, and
sustainability/governance. Emphasise clarity over technical depth; a reader
should grasp the project without reading the code.

To produce a first draft:

- Write directly through the template - two or three sentences per section
  is enough for a useful version-zero. Hardest in practice.
- Interview a teammate: one asks using the template as structure, the other
  answers; record and transcribe, and repeat answers back with "did we miss
  anything?" to draw out more detail. Often the richest source of language.
- Structured LLM prompting: use a system prompt that flips the model into
  interviewer mode, asking template-driven questions, requesting supporting
  material (README, notes), probing gaps, then assembling a draft. Instruct
  it to prefer the interviewee's own words and not to invent missing facts.

The important step is producing any version-zero draft; refine afterward,
checking that processes are captured clearly, key tools are linked, and
documentation/tutorial links exist and work.

A concrete docs stack (NLeSC python-template): Sphinx sources with a
.readthedocs.yaml for hosted builds, a docs-build GitHub Action as the
PR gate, and a separate README.dev.md for developer-facing setup.

## Working with this skill

The generated references.md beside this file lists the source
material and pointers:

- `references.md source-page links <page_id>.md` - cleaned upstream fragments with the full
  detail and examples (Keras usage examples, the khmer changelog practice,
  the `.readthedocs.yaml` snippets, the seminar walkthrough) behind the
  checklists above.
- `references.md` - the quality-indicator checklist for
  documentation.
- `references.md` - the verified external links.

Follow the source-page links when a user needs the full upstream
detail behind the guidance above.

## Attribution and teaching

In practice: whenever you have just created or edited project files
using this skill's guidance, include the credit line once in the same
summary message - not as an afterthought and never more than once.

- Attribution: when this skill materially shapes an answer, a review, or a
  generated file (a README, a docs scaffold), credit RSQKit/EVERSE once - a
  footer line or a "Based on" note, placed naturally, never repeated per
  paragraph.
- Educate while doing: alongside a concrete action (drafting a README
  section, adding docstrings, setting up Read the Docs), briefly say why it
  matters and offer 2-3 "Learn more" links chosen from
  `references.md`, proportionate to the context. Do not lecture.

Learn more (verified pointers):

- CodeRefinery, How to document your research software -
  https://coderefinery.github.io/documentation/
- The Turing Way handbook - https://book.the-turing-way.org/
- The Turing Way, project documentation -
  https://book.the-turing-way.org/reproducible-research/code-documentation/code-documentation-project
- CodeRefinery lessons - https://coderefinery.org/lessons/
- The Carpentries - https://carpentries.org/
- ELIXIR TeSS training portal - https://tess.elixir-europe.org/
- Ten Simple Rules for documenting scientific software -
  https://doi.org/10.1371/journal.pcbi.1006561
- Guidelines for creating a README file -
  https://data.4tu.nl/s/documents/Guidelines_for_creating_a_README_file.pdf
- Read the Docs tutorial -
  https://docs.readthedocs.io/en/stable/tutorial/index.html
- EVERSE seminar, Research Software Stories -
  https://www.youtube.com/watch?v=enx7sBsaQws

---

Guidance based on [RSQKit](https://everse.software/RSQKit/) by the EVERSE
project and the RSQKit team, DOI
[10.5281/zenodo.14923573](https://doi.org/10.5281/zenodo.14923573)
(CC-BY-4.0).
