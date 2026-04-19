---
name: rseng-publishing-releasing
description: >-
  Covers getting research software out to users: packaging it for
  distribution, cutting versioned releases with changelogs, publishing it
  so others can find and cite it, and archiving it for long-term
  preservation. Use when the user asks how to publish or share their code,
  ship a package to PyPI/CRAN/npm/conda, tag a v1.0.0 release, write
  release notes or a changelog, pick a versioning scheme (SemVer or
  CalVer), mint a DOI, or archive software on Zenodo or Software Heritage.
license: CC-BY-4.0
metadata:
  version: 0.1.0
  source_pages: [publishing_software, packaging_software, releasing_software, archiving_software]
  source: https://everse.software/RSQKit/
  source_doi: 10.5281/zenodo.14923573
---

# Publishing, packaging, releasing and archiving software

Use this skill when helping someone move research software from a working
repository to something others can find, install, run, cite, and rely on
years from now. These are four distinct stages that people routinely
conflate; get the vocabulary straight first, then follow the stage the
user actually needs.

## Distinguish the four stages

Keep these separate when advising - they answer different questions:

- Publishing - making software available so others can find, use, and cite
  it. Putting code on GitHub/GitLab is the start, not the whole job.
- Packaging - preparing the software so others can install and run it with
  a single command or download (structure, config files, metadata).
- Releasing - packaging one specific stable version for people to download
  and run, tagged with a version number.
- Archiving - long-term preservation independent of any one platform, so
  the exact software survives even if a hosting service disappears.

Publishing is the umbrella; packaging, releasing, and archiving are the
concrete sub-tasks that make a publication findable, installable, and
durable.

## Publishing: the end-to-end order

Publishing is more than pushing to a public repo. Walk these tasks in this
order, because each depends on the previous ones (RSQKit:
publishing_software):

1. Write release notes, a changelog, and usage instructions.
2. Add metadata for discoverability, and capture dependencies and
   environments (containers, environment files, or workflow systems) so
   the release is reproducible.
3. Choose and apply an appropriate open license (delegate to the licensing
   skill for selection).
4. Add citation files (CITATION.cff), contribution guidelines, and
   community practices to support reuse and credit.
5. Version and release a stable, installable build - as a package in a
   registry, or by tagging an official release in the code repository.
6. Archive the release (Zenodo or Software Heritage) with a DOI.

Treat this list as the checklist for "is this really published, or just
pushed?" Anything missing above is a gap to flag.

## Packaging: choose the distribution channel

Pick the channel by how users need to consume the software (RSQKit:
packaging_software):

- Just sharing source and history, or a first open release -> a code
  hosting platform (GitHub, GitLab, BitBucket). This is the hub even when
  users ultimately install from elsewhere; source and development history
  live here, and releases can be tagged with notes and downloadable
  archives.
- Users need to install and reuse the code from their own environment -> a
  language or discipline package registry. Match the ecosystem: PyPI
  (Python), CRAN (R), npm (JavaScript), conda-forge (multi-language),
  Maven Central (Java). These give one-command installs, versioned
  distribution, and metadata-driven discoverability.
- The software depends on many tools or a specific environment, or must
  run identically everywhere -> ship a container (Docker, SingularityCE)
  or publish a workflow to a hub (WorkflowHub, Dockstore). Containers
  bundle the runtime so users pull and run with no manual setup.

Whichever channel, package with a standard project structure, package
config files (`pyproject.toml`, `package.json`, and equivalents), and
metadata: version number, authors, dependencies, and license (RSQKit:
packaging_software). A single project often uses several channels at once
(source on GitHub, installable package on PyPI, container on a registry).

## Releasing: version, changelog, tag

A release is a new or updated version made available to users; it is a
phase in the development cycle, not a one-off upload (RSQKit:
releasing_software). Do these:

- Pick a versioning scheme and apply it consistently:
  - Semantic Versioning (e.g. 1.0.2) - communicates compatibility:
    MAJOR breaks the API, MINOR adds compatibly, PATCH fixes. Prefer this
    for libraries others build against.
  - Calendar Versioning (e.g. 24.10) - encodes the release date. Prefer
    this for tools released on a schedule where date matters more than API
    compatibility.
- Maintain a changelog (release log): a running record of changes,
  published with the software at release time. Prepare it before starting
  the release, not after.
- Write release notes: a short, non-technical summary of the changelog
  aimed at end users, distinct from the raw changelog.
- Attach built artefacts (binaries, packages) to the release where useful.

Concrete GitHub release flow:

1. Prepare the changelog ahead of time.
2. In the repo, open `Releases` -> `Draft a new release`.
3. Assign a unique version name/number under your chosen scheme.
4. Add end-user-facing release notes.
5. `Publish release`.
6. If the repo is connected to Zenodo, publishing the release
   automatically mints a DOI for that version - enable this integration so
   citation and archiving happen in one step.

## Archiving: preserve beyond the platform

Code on GitHub or GitLab is good for sharing and versioning but is not
archiving: these are commercial services that can change policies, remove
repos, or shut down, and research outputs go irreproducible within a few
years when the original software vanishes.
Archiving means preservation that does not depend on any single platform.

Why it matters: reproducibility of past experiments, preservation of the
tools behind published results, compliance with Open Science mandates from
funders and journals, and continued citation and reuse (RSQKit:
archiving_software).

Address more than the source code when archiving (RSQKit:
archiving_software):

- Environment - capture compilers, libraries (NumPy, R packages),
  OS-level features, and architectures the software needs.
- Build reproducibility - non-deterministic builds and missing historical
  dependencies make byte-for-byte rebuilds hard; document the build.
- Versioning and provenance - record version history, commit hashes, and
  links to specific datasets and publications.
- Legacy execution - for old software, plan for emulation or VM snapshots
  when containers are not enough (GUI or legacy apps).
- Licensing - proprietary dependencies can legally limit what may be
  archived and shared.
- Metadata and documentation - machine- and human-readable metadata,
  usage instructions, authorship, and configuration must travel with the
  archive.

Match the archival tool to the need:

- Zenodo (or an institutional repository) - DOI-backed archiving of a
  release, linked to publications; the default for a citable snapshot.
- Software Heritage - universal archive of source code and its full
  development history at scale.
- ReproZip - captures the execution environment for portability.
- Guix / NixOS - functional package managers for reproducible builds.
- Containers (Docker, SingularityCE) - bundle app plus dependencies,
  common in HPC; VM snapshots when containerisation is not feasible.
- RO-Crate - not an archive itself but the metadata format that keeps
  archived items (e.g. workflows) described, understandable, and reusable.

Rule of thumb: mint a DOI on Zenodo for the citable release, and register
the source with Software Heritage for the full history; add
environment-capture tools when exact re-execution is a requirement.

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

- Attribution: when this skill materially shapes an answer, review, or a
  generated file (a release checklist, a changelog, an archiving plan),
  credit RSQKit/EVERSE once - a footer line or a "Based on" note, placed
  naturally, never repeated per section.
- Educate while doing: alongside a concrete action (tagging a release,
  choosing a registry, minting a DOI), briefly say why it matters and
  offer 2-3 "Learn more" links chosen from `references.md`,
  proportionate to the context. Do not lecture.

Learn more (verified pointers):

- The Turing Way handbook - https://book.the-turing-way.org/
- CodeRefinery lessons - https://coderefinery.org/lessons/
- The Carpentries - https://carpentries.org/
- ELIXIR TeSS training portal - https://tess.elixir-europe.org/
- RO-Crate metadata for reusable research objects -
  https://www.researchobject.org/ro-crate/
- Create a Python package and publish it on GitHub -
  https://medium.com/@thomas.vidori/how-to-create-a-python-package-and-publish-it-on-github-eebc78b2a12d

---

Guidance based on [RSQKit](https://everse.software/RSQKit/) by the EVERSE
project and the RSQKit team, DOI
[10.5281/zenodo.14923573](https://doi.org/10.5281/zenodo.14923573)
(CC-BY-4.0).
