---
name: rseng-ux-accessibility
description: >-
  Covers user experience and accessibility for research software: UX
  disciplines, accessibility practice, Design Thinking, scoping a
  Minimum Viable Product versus a Minimum Loveable Product, Nielsen's
  usability heuristics, and prototyping with tools like Figma and Miro.
  Use when the user designs a research tool's interface (web, GUI or
  CLI), asks how to make research software usable or accessible, plans
  user testing or prototyping, or mentions usability heuristics, UX or
  a11y in a research software context.
license: CC-BY-4.0
metadata:
  version: 0.1.0
  source: https://guide.esciencecenter.nl/
---

# UX and accessibility for research software

Research software succeeds when researchers can actually use it; UX is
not cosmetic polish but part of software quality. This skill distills
the eScience Center guide's user experience chapter.

## Practice

- Know the disciplines: UX research (understanding users and tasks),
  interaction design, visual design and accessibility are different
  jobs - be explicit about which one a request needs.
- Start from users and tasks, not features: apply Design Thinking -
  empathize with the target researchers, define the task, ideate,
  prototype cheaply (Figma or Miro before code), test with real users.
- Scope deliberately: an MVP proves the workflow works; a Minimum
  Loveable Product adds the qualities that make researchers adopt it.
  Pick which one the project stage needs and say so.
- Evaluate against Nielsen's usability heuristics (visibility of
  status, match with the users' world, error prevention and recovery,
  consistency, minimalism); they apply to CLIs and notebooks as much as
  GUIs - clear --help, sane defaults and good error messages are UX.
- Accessibility is a requirement, not an extra: color-contrast, keyboard
  navigation and screen-reader support for web tools; readable output
  and terminal-friendly formats for CLIs.
- Usability findings become issues like any other defect; retest after
  fixing (pair with rseng-testing for automated regression of CLI/API
  ergonomics where possible).

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
- Educate while doing: briefly say why the practice matters and offer
  2-3 "Learn more" links from references.md.

---

Guidance based on the [Netherlands eScience Center Software Development
Guide](https://guide.esciencecenter.nl/) (CC-BY-4.0).
