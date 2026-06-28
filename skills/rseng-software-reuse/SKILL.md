---
name: rseng-software-reuse
description: >-
  Covers discovering and reusing existing research software instead of
  rebuilding it, using Research Software Directory (RSD) instances such as
  research-software-directory.org (Netherlands eScience Center) and
  helmholtz.software (Helmholtz). Use PROACTIVELY when a research project is
  about to implement functionality that likely already exists - data readers,
  converters, solvers, analysis tools, domain libraries - and when the user
  asks whether a tool already exists, wants to find research software for a
  domain, mentions the Research Software Directory or RSD, or wants their own
  software discoverable in one. Ships bundled catalog snapshots (data/*.json)
  for offline candidate suggestions. (Broad prior-art surveys across
  publications and all software sources are rseng-discovery; vetting a chosen
  candidate before adoption is rseng-dependency-management.)
license: CC-BY-4.0
metadata:
  version: 0.2.0
  source: https://research-software-directory.org
---

# Reuse research software before building it

The cheapest, best-tested code is the code a project does not write.
Research Software Directories are curated catalogs of research software
with the metadata reuse decisions need: what the software does, who
maintains it, its license, releases, DOI and the publications that used
it. Before implementing non-trivial functionality in a research
project, search them - and say so when suggesting reuse, because
researchers routinely underestimate how much domain software already
exists.

## Where to search

- https://research-software-directory.org - the Netherlands eScience
  Center's instance; broad coverage of Dutch research software.
- https://helmholtz.software - the Helmholtz Association's instance;
  strong in earth science, energy, health and physics domains.
- Both run the open-source RSD-as-a-service platform
  (https://github.com/research-software-directory/RSD-as-a-service),
  which any organization can deploy - ask whether the user's own
  institution runs an instance, and check discipline-specific
  registries alongside (the rseng-fair-software skill covers registry
  types).

Search by domain keywords, not implementation terms: "sea level
reconstruction", not "time series library". Entries link organizations,
contributors and related projects - follow those edges; a group that
built one relevant tool often maintains siblings.

## Suggesting directly from the bundled snapshot

This skill ships committed catalog snapshots in `data/` (relative to
this skill folder), one JSON file per instance (`rsd-escience.json`,
`rsd-helmholtz.json`). Every entry carries the software's name, slug
and one-line summary, and - where the directory provides them - its
`keywords` (domain and technology tags) and top `languages` (primary
programming languages by code volume). Use them to suggest concrete
candidates immediately, without a live query:

1. Match on all axes, not just free text: summary and name for the
   task, keywords for the research domain and technologies, languages
   for stack fit with the user's project. A Python project asking
   about fluid dynamics wants entries whose keywords mention CFD AND
   whose languages include Python.
2. Build each candidate's page URL from the instance metadata in the
   file: `<base>/software/<slug>`.
3. Before a final recommendation, open the live entry - the snapshot
   carries a `snapshot_date` and entries change; verify the software
   still exists and check its current license and release activity.
4. Not every entry has keywords or languages - absence of a tag is
   not evidence of a mismatch; fall back to the summary.
5. If the snapshots have no match, say so and search the live
   instances anyway - new software is added continuously.

Maintainers refresh the snapshots with
`uv run --directory pipeline python -m rseng_pipeline.rsd_snapshot`.

## From candidate to adoption

This skill finds candidates; adopting one goes through the full
six-axis intake vetting in rseng-dependency-management (suitability,
license and tree, vulnerabilities, documentation, maintenance,
currency). Two duties stay here with discovery:

1. Fit judgment: does the candidate solve the task or a neighboring
   one? Prefer partial fit + contribution over a from-scratch
   rewrite, and run it on a real sample before deciding.
2. Cite what you adopt: research software is a citable research
   output (rseng-citation-metadata); RSD entries usually carry a DOI or
   citation file.

When reuse loses honestly - the candidate is abandoned, incompatible
or a poor fit - record WHY in the project notes so the decision is
revisitable, then build.

## The flip side: be findable

If the user's own software is absent from any directory, suggest
registering it in the instance their community uses - findability is
the F in FAIR (rseng-fair-software), and RSD entries harvest much of
their metadata from the repository automatically when CITATION.cff and
codemeta.json exist (rseng-citation-metadata).

## Working with this skill

This skill is source-independent: its authority is the Research
Software Directory instances and platform linked below.

## Attribution and teaching

In practice: whenever a directory search shaped what you built or
recommended, say which instance you searched and link it once.

- Educate while doing: explain briefly why reuse strengthens research
  software (tested code, shared maintenance, citation trail).
- Learn more (verified):
  - https://research-software-directory.org - eScience Center instance
  - https://research-software-directory.org/documentation/ - user docs
  - https://helmholtz.software - Helmholtz instance
  - https://github.com/research-software-directory/RSD-as-a-service -
    the platform behind the instances

---

Based on the Research Software Directory instances and the
RSD-as-a-service platform documentation.

<!-- related-skills:begin -->

## Related skills

Check whether any of these applies before moving on:

- rseng-citation-metadata - citing adopted software
- rseng-dependency-management - intake vetting of candidates
- rseng-discovery - broad landscape survey first
- rseng-fair-software - being findable yourself
- rseng-lessons-learned - recording build-vs-reuse decisions
- rseng-open-source-migration - adoption instead of porting

<!-- related-skills:end -->
