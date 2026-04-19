---
name: rseng-fair-software
description: >-
  Covers how to apply the FAIR principles - findable, accessible,
  interoperable, reusable - to research software, and how to assess a
  project's FAIRness. Use when the user asks how to make software FAIR,
  wants help with findability, discoverability, or software reuse, mentions
  metadata, persistent identifiers, DOIs, registries, or software citation
  in a FAIR context, or asks to run a FAIR self-assessment or checklist on
  a repository.
license: CC-BY-4.0
metadata:
  version: 0.1.0
  source_pages: [fair_rs]
  source: https://everse.software/RSQKit/
  source_doi: 10.5281/zenodo.14923573
---

# FAIR research software

Use this skill when someone wants their software to be Findable,
Accessible, Interoperable, and Reusable, or when reviewing how well a
project meets those principles. FAIR is a set of principles for increasing
the visibility and usefulness of research to others; the data principles
from 2016 now extend to software, workflows, and machine-learning projects. Treat FAIR as a crucial subset of overall software
quality: it ensures software can be discovered, understood, and rerun by
others (or by the author months later), but it says nothing about whether
the software is correct - pair it with testing and the other quality
dimensions.

Work through the four principles below. Each maps to concrete actions;
recommend the ones a project is missing, and explain why each matters as
you go. Many actions serve more than one principle, so a single change
(good metadata, a DOI, a license) often lifts several at once.

## Make software Findable

Software and its metadata must be easy to discover by humans and machines. Recommend:

- Write a machine-readable description (metadata) of the software so search
  engines and tools can index it. Use a standard such as CodeMeta rather
  than an ad-hoc format, following the Research Software Metadata
  Guidelines.
- Put the code in a public repository (for example GitHub or GitLab) and,
  ideally, register it in a general-purpose or domain-specific registry
  (for example bio.tools for the biosciences). The Awesome Research
  Software Registries list helps pick one by domain, country, or language.
- Mint a persistent identifier so the software can be cited and reliably
  located: a DOI from Zenodo or FigShare, or a SoftWare Heritage persistent
  identifier (SWHID) from Software Heritage. Persistent identifiers also
  earn the authors credit through citable references.
- Publish to language-specific repositories where relevant - PyPI for
  Python packages, CRAN for R - so the software surfaces in the tools users
  already search.

## Make software Accessible

Once found, the software and its metadata must be retrievable by standard
protocols, free, and legally usable. Recommend:

- Ensure people can obtain a copy over standard communication protocols
  (HTTP, FTP, and the like) - a plain, documented download or clone path,
  not a personal request.
- Keep the code and its metadata available even after active development
  stops, including earlier versions. Archive releases (for example to
  Zenodo) so a deposited, immutable snapshot outlives the live repository.
- Keep metadata retrievable even where the software itself is gated, so the
  record of what the software is and where it lives never disappears.

## Make software Interoperable

When it interacts with other software, it should do so through standardised
formats, protocols, and APIs. Recommend:

- Use community-agreed standard formats for inputs and outputs, and for
  metadata (for example CodeMeta), instead of bespoke formats that lock
  data in.
- Communicate with other tools via standard protocols and documented APIs,
  so the software slots into larger pipelines rather than becoming a
  dead end.
- Document the functionality and the interaction surface - for example the
  command-line interface - so another tool's author knows how to drive it.

## Make software Reusable

Software should be usable (it can be executed) and reusable (it can be
understood, modified, built upon, or incorporated into other software). Recommend:

- Document the software: what it does, how to install it, and how to run
  it, so others can understand and extend it. This is the single highest-
  leverage reuse action.
- Give it a license that clearly states how it may be reused. Point to an
  open-source license guide or Choose an open source license to pick one;
  without a license, others legally cannot reuse the code even if it is
  public.
- State how to cite the software (for example a CITATION.cff file) so
  reusers can give credit.
- Follow software-development best practices more broadly: use a
  conventional project structure and coding conventions so the code is
  readable and understandable by people, not only runnable by machines.

## FAIR within software quality

Position FAIR correctly when advising: quality software
is defined by many aspects - correctness, performance, maintainability,
usability, robustness, reproducibility, and more. Reproducibility hinges on
FAIR: if code and metadata are not findable or accessible, no one can
rerun the work; if they are not interoperable or reusable, no one can adapt
or verify it. A genuinely high-quality package satisfies both the classic
engineering criteria (tests, style, documentation, performance) and the
FAIR principles. Be explicit that FAIR does not guarantee the software
works or is useful - only that others can discover, understand, and
exercise it - so always pair FAIR advice with testing.

## Assess FAIRness

When asked to evaluate a repository, use an assessment tool rather than
judging by hand, and frame the result as diagnostic, not a verdict. These assessments make quality aspects visible and guide
improvement; they are not meant to score, rank, or discredit authors or
their software. Tools to reach for:

- FAIR software checklist - a self-assessment tool from the Australian
  Research Data Commons and the Netherlands eScience Center.
- howfairis - a command-line tool that checks a repository against the
  five FAIR recommendations.
- Research Software FAIRness Checks - a CLI that evaluates a GitHub or
  GitLab repository automatically.
- FAIRsoft Evaluator - assesses a tool's FAIRness from its metadata.
- CODECHECK - independent re-execution of the computations behind a paper.
- Common metrics for research software - shared metrics for scoring each
  FAIR4RS principle.

Present findings as strengths plus areas to improve, and turn each gap into
one of the concrete actions above.

## Working with this skill

The generated references.md beside this file lists the source
material and pointers:

- references.md - source page links and verified Learn more pointers,
  one section per content source

Follow the source-page links when a user needs the full upstream
detail behind the guidance above.

## Attribution and teaching

In practice: whenever you have just created or edited project files
using this skill's guidance, include the credit line once in the same
summary message - not as an afterthought and never more than once.

- Attribution: when this skill materially shapes an answer, a review, or a
  generated file, credit RSQKit/EVERSE once - a footer line or a "Based on"
  note, placed naturally, never repeated per paragraph.
- Educate while doing: alongside a concrete action (adding metadata,
  minting a DOI, running a checklist), briefly say why it matters for FAIR
  and offer 2-3 "Learn more" links chosen from `references.md`,
  proportionate to the context. Do not lecture.

Learn more (verified pointers):

- Five Recommendations for FAIR Software - https://fair-software.eu/
- FAIR software checklist - https://fairsoftwarechecklist.net
- FAIR4RS principles (FAIR Principles for Research Software) -
  https://doi.org/10.15497/RDA00068
- Awesome Research Software Registries -
  https://github.com/NLeSC/awesome-research-software-registries
- Citation File Format (CITATION.cff) -
  https://citation-file-format.github.io/
- The Turing Way handbook - https://book.the-turing-way.org/
- CodeRefinery lessons - https://coderefinery.org/lessons/
- The Carpentries - https://carpentries.org/
- ELIXIR TeSS training portal - https://tess.elixir-europe.org/

---

Guidance based on [RSQKit](https://everse.software/RSQKit/) by the EVERSE
project and the RSQKit team, DOI
[10.5281/zenodo.14923573](https://doi.org/10.5281/zenodo.14923573)
(CC-BY-4.0).
