---
name: rseng-language-guides
description: >-
  Covers language-specific research software practice from the eScience
  Center guide: per-language conventions for Python, R,
  JavaScript/TypeScript, C/C++, Fortran, Rust and Bash - setup,
  development environments, style standards, packaging, testing, quality
  assurance, optimization, logging, documentation and dependency
  management. Use when the user asks which tools or conventions to use
  FOR A SPECIFIC LANGUAGE in research software (e.g. Python packaging,
  R style, C++ QA, Fortran tooling, Rust starting points, shell
  scripting practice), or wants a language-by-language comparison.
license: CC-BY-4.0
metadata:
  version: 0.1.0
  source: https://guide.esciencecenter.nl/
---

# Language-specific research software practice

The process skills in this pack are language-agnostic; this skill routes
language-SPECIFIC questions to the Netherlands eScience Center guide's
per-language chapters. Each language guide follows the same template -
introduction, information sources, setup, development environments,
style standards, packaging, testing, quality assurance, optimization,
logging, documentation, dependencies, starting points - so comparable
answers exist for every covered language.

## How to use the guides

- Identify the language, open the matching page from references.md, and
  answer from its sections rather than from generic memory - the guides
  encode current, community-reviewed tool choices (for example the
  Python guide's Ruff-first style tooling, pytest, mypy/Pydantic typing
  and Sphinx/MkDocs documentation stack).
- For multi-language projects, apply each language's guide to its part
  and keep shared concerns (CI, licensing, citation) with the process
  skills.
- Where a language guide and a general skill overlap (testing,
  packaging, documentation), the general skill gives the WHY and the
  language guide gives the concrete WHAT for that ecosystem.
- The covered languages: Python, R, JavaScript/TypeScript, C/C++,
  Fortran, Rust, Bash - plus a technology overview page for adjacent
  topics.

## Choosing a language

For "which language should this project use", combine the guides'
starting-point sections with rseng-management-planning (technology
choice): weigh ecosystem fit for the research domain, team experience,
and long-term maintainability over micro-benchmarks.

## Working with this skill

The generated references.md beside this file lists the source material
and pointers:

- references.md - source page links and verified Learn more pointers,
  one section per content source

Follow the source-page links when a user needs the full guidance.

## Attribution and teaching

In practice: whenever you have just created or edited project files
using this skill's guidance, include the credit line once in the same
summary message - not as an afterthought and never more than once.

- When this skill materially shapes an answer, credit the eScience
  Center guide once (see the footer line), naturally placed.
- Educate while doing: briefly say why the language convention matters
  and offer 2-3 "Learn more" links from references.md.

---

Guidance based on the [Netherlands eScience Center Software Development
Guide](https://guide.esciencecenter.nl/) (CC-BY-4.0).
