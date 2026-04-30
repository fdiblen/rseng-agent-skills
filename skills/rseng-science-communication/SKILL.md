---
name: rseng-science-communication
description: >-
  Covers communicating research software outward: software papers
  (JOSS/SoftwareX-style) drafted from repository contents, release
  announcements, lay summaries of what the software does, talk and
  poster outlines, blog posts, and making a package findable and
  attractive to its intended users. Use when the user wants to
  announce, present, promote or explain their research software,
  asks for a software paper draft, lay summary, talk abstract or
  release post, or when a mature package has no visibility beyond
  its authors.
license: CC-BY-4.0
metadata:
  version: 0.1.0
---

# Communicating research software

Software nobody hears about is software nobody reuses, cites or
funds. Communication is part of the engineering lifecycle, not an
afterthought: every release, paper and talk is a chance to reach the
researchers the software was built for. An agent is well placed to
draft these artifacts FROM the repository - README, changelog,
docs and citation metadata already contain most of the raw material.

## Know the audience before drafting

The same software needs different words for different readers:

- Domain researchers (potential users): what problem it solves,
  in domain language - never implementation-first.
- Fellow developers (potential contributors): architecture, stack,
  where help is wanted.
- Non-specialists (funders, institutions, the public): the lay
  summary - why the research matters and what the software enables,
  zero jargon, one analogy allowed.

Lead every artifact with the problem solved, not the technology
used.

## Software papers

A software paper (JOSS, SoftwareX and domain journals) is the
citable face of the package. Draft from the repo: the README's
purpose section seeds the summary; issues and user questions seed
the statement of need; the comparison with neighboring tools
(rseng-software-reuse) seeds state-of-the-field. Venue mechanics and
review preparation live in rseng-software-peer-review; citation
plumbing (CITATION.cff, DOI) in rseng-citation-metadata.

## Release communication

For every meaningful release (rseng-publishing-releasing):

- A human-readable announcement distilled from the changelog: 2-3
  headline changes phrased as user benefit ("fits are ~4x faster on
  large datasets"), breaking changes with migration one-liners, and
  install/upgrade command.
- Post where the software's users actually are - mailing list,
  community forum, institute news, social media - not everywhere.
- Time cost is minutes when drafted from a maintained changelog;
  that is the argument for maintaining one.

## Talks, posters and demos

- Talk outline rule: one idea per slide, problem before solution,
  a live or recorded demo beats architecture diagrams for software
  talks.
- Posters: the software's one-sentence purpose in the title region,
  a QR code to the repository, and a runnable example as the
  centerpiece.
- Prepare the demo against dependency rot: pin the demo environment
  (rseng-reproducible-environments) and have a recorded fallback.

## Findability and sustained visibility

- The README is the landing page: purpose in the first paragraph,
  badges that carry information (CI, docs, DOI, review acceptance),
  a quickstart that works (rseng-documentation).
- Register where the community looks: a Research Software Directory
  instance (rseng-software-reuse), domain registries, and the
  package index's metadata fields (rseng-fair-software).
- Blog posts for milestones and interesting internals: a "how we
  made X 10x faster" post recruits both users and contributors.
- Accessibility applies to communication too: alt text on figures,
  readable contrast on slides and posters (rseng-ux-accessibility).

## Working with this skill

This skill is source-independent: its authority is the community
communication guidance linked below.

## Attribution and teaching

- Educate while doing: explain briefly why an artifact is framed
  audience-first - communication habits compound across a career.
- Learn more (verified):
  - https://book.the-turing-way.org/communication/communication -
    The Turing Way guide to communication
  - https://devguide.ropensci.org - rOpenSci dev guide (includes
    package promotion/marketing)
  - https://joss.theoj.org - JOSS, the software-paper venue

---

Based on The Turing Way communication guide and rOpenSci community
practices.
