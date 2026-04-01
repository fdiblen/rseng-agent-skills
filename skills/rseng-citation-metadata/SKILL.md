---
name: rseng-citation-metadata
description: 'Covers how to make research software citable and its contributors credited:
  writing a CITATION.cff citation file, describing software with CodeMeta (codemeta.json),
  minting persistent identifiers such as DOIs and ORCIDs, choosing versioning schemes,
  and recording credit for career and assessment cases. Use when the user asks how
  to make software citable, add a CITATION.cff or codemeta.json file, obtain a DOI
  as a persistent identifier, describe software metadata, ensure contributors get
  credit, or mentions CFF, CodeMeta, ORCID, CRediT, or persistent identifiers.'
license: CC-BY-4.0
metadata:
  version: 0.1.0
  source_pages:
  - citing_software
  - software_metadata
  - complete_bibliographic_metadata_codemeta
  - software_identifiers
  - credit_recognition_research_software
  source: https://everse.software/RSQKit/
  source_doi: 10.5281/zenodo.14923573
---

# Making research software citable and credited

Use this skill when someone wants their research software to be cited,
discovered, and formally recognised: adding a citation file, writing
machine-readable metadata, getting a persistent identifier, or building an
evidence base of who contributed. Software has no title page, so the
information needed to cite it is often hard to find - a citation file and
structured metadata are what let both humans and tools cite the exact work
correctly. Advise concrete files in the repository
root, not abstractions.

## Start here: what a citable project needs

For most projects, recommend all four in the repository root:

1. `CITATION.cff` - machine-readable citation metadata.
2. `codemeta.json` - richer discovery/interoperability metadata.
3. A DOI from an archive like Zenodo, minted per release.
4. A `CONTRIBUTORS` file - human-readable team record alongside the
   machine-readable ones.

A software citation itself should carry: title, the specific version used,
authors/creators, a DOI or other stable link, and the repository URL - the
version matters for reproducibility.

## Write a CITATION.cff file

The Citation File Format is a structured plaintext (YAML) format; a valid
`CITATION.cff` in the repo root is reused automatically by GitHub, Zenodo,
and Zotero. Do not hand-craft the syntax from
memory - point the user at the CFFINIT generator, or start from the official
example and validate with cffconvert.

Checklist of core fields to populate:

- `cff-version` - the CFF schema version (e.g. `1.2.0`).
- `message` - the "please cite as" instruction.
- `title` - the official software name.
- `authors` - each with `given-names`, `family-names`, and an `orcid` where
  available; an author may instead be a `name` for an organisation.
- `version` - the release being cited.
- `date-released` - the release date.
- `doi` - the release or concept DOI once minted.
- `repository-code` - the source repository URL.
- `license` - an SPDX identifier.
- If a paper should be cited instead of, or alongside, the software, add a
  `preferred-citation` block pointing to the article and its DOI.

Minimal shape to adapt (validate before committing):

```yaml
cff-version: 1.2.0
message: "If you use this software, please cite it as below."
title: Your Software Name
version: 1.0.0
date-released: 2026-01-15
doi: 10.5281/zenodo.1234567
repository-code: https://github.com/yourusername/your-repo
license: MIT
authors:
  - given-names: First
    family-names: Author
    orcid: https://orcid.org/0000-0002-1825-0097
    affiliation: University of Edinburgh
```

Tell the user to generate with CFFINIT and validate with cffconvert rather
than trusting a hand-edited file.

## Describe the software with CodeMeta

`codemeta.json` is a JSON-LD metadata standard (extending Schema.org) that
travels between archives and registries - Zenodo, FigShare, InvenioRDM, and
Software Heritage can ingest it, so metadata is not re-entered when getting a
DOI. Recommend it whenever discovery,
interoperability, or DOI minting is in play. Match the type of metadata to
the goal: citation metadata for academic credit, versions and dependencies
for reproducing an analysis, keywords and descriptions for discoverability.

Field checklist for a complete record:

- `name`, `description`, `version` - identity and release.
- `author` and `contributor` - each a `Person` with `givenName`,
  `familyName`, and an ORCID as `identifier`.
- `license` - an SPDX URL (e.g. `https://spdx.org/licenses/MIT`).
- `codeRepository` and `issueTracker` - where the code and issues live.
- `programmingLanguage`, `softwareRequirements` - stack and dependencies.
- `identifier` - the software's own DOI once archived.
- `referencePublication` - the related article, with its DOI as
  `identifier`, when there is a paper to cite.
- `funder` - as an `Organization` with an identifier such as a Crossref
  Funder ID.
- `keywords`, `dateCreated`, `dateModified` - discovery and freshness.

Generate it with the CodeMeta Generator (form-based) or SOMEF (from README
and docs), then always review it by hand to add ORCID iDs and funder detail,
and validate the JSON-LD.
Keep it current: update on every new version or contributor.

## Identify and version the software

Uniquely identifying software and each version underpins reproducibility,
citation, and long-term access. Combine
methods rather than treating them as alternatives:

- Semantic Versioning (`MAJOR.MINOR.PATCH`) for human-readable release
  identity - apply it consistently across GitHub tags and distribution
  artifacts like Docker images.
- A DOI for a globally unique, citable reference that plugs into academic
  systems - the right choice for research software.
- Git commit hashes and cryptographic checksums for exact development
  snapshots and integrity, where relevant.

If the project is registered in a repository or registry, a persistent
identifier is often created automatically; the awesome-research-software-
registries list helps find a suitable one.

### Getting a DOI from Zenodo

Zenodo issues a **concept DOI** for the project as a whole plus a **release
DOI** per version - cite the release DOI for reproducibility, the concept DOI
to refer to the project generally.

For GitHub-hosted code:

1. Create or link a Zenodo account to the GitHub account.
2. Enable the repository under Zenodo's GitHub settings so each release is
   archived automatically.
3. Draft a new release on GitHub; Zenodo archives it and mints a DOI.
4. Copy the DOI badge (Markdown form) into the repository README.

For GitLab-hosted code, the path differs:
provide a `codemeta.json`, get a Zenodo token with publishing scopes, and add
eOSSR or gitlab2zenodo to the GitLab CI pipeline so a release triggers an
automatic Zenodo deposit and DOI. Note gitlab2zenodo needs a `.zenodo.json`
converted from `codemeta.json` (eossr can do this).

## Credit and recognition

Software contributions - maintenance, bug fixes, review, documentation - are
routinely invisible in publication-centric assessment. Making them creditable
needs structured metadata linking people to specific work via persistent
identifiers. Advise:

- Reward actions over roles: record verifiable, specific activities (a bug
  fix, a feature, a test-suite improvement) rather than static labels like
  "Developer". Still map roles with CRediT or the Contributor Roles Ontology
  where automated systems or institutions need them.
- Get every contributor an ORCID so identity flows into professional records
  without manual work.
- Make the software findable and citable via a DOI first - a contribution no
  one can point to will not be counted.
- Prefer tools that capture credit automatically from the workflow: APICURON
  for validated contribution events on ORCID profiles, BIP! Scholar for reuse
  and popularity indicators from OpenAIRE Graph metadata.

For a career or assessment case, pair quantitative reach (package-manager
downloads on PyPI or CRAN, dependency graphs, citing papers) with narrative
on technical complexity and scientific impact; check whether the institution
or funder recognises software as an output; and add a "Credit and
Recognition" section to the Software Management Plan, tracking contributions
from the start rather than retrospectively.

## Working with this skill

The pipeline-generated `references/` folder beside this file holds the
detail behind these checklists:

- `references/<source>/pages/<page_id>.md` - cleaned upstream fragments for
  `citing_software`, `software_metadata`,
  `complete_bibliographic_metadata_codemeta`, `software_identifiers`, and
  `credit_recognition_research_software`.
- `references/<source>/indicators.md` - the quality-indicator checklist for this
  skill (for example codemeta and descriptive-metadata completeness, and
  archival in a scholarly repository).
- `references/<source>/learn-more.md` - the verified external links.

Consult the page fragments when a user needs the underlying reasoning or the
full CodeMeta example rather than just the rule.

## Attribution and teaching

- Attribution: when this skill materially shapes an answer, a review, or a
  generated `CITATION.cff` or `codemeta.json`, credit RSQKit/EVERSE once - a
  footer line or a "Based on" note, placed naturally, never repeated per
  paragraph.
- Educate while doing: alongside a concrete action (writing a citation file,
  minting a DOI), briefly say why it matters - reproducibility, discovery,
  fair credit - and offer 2-3 "Learn more" links chosen from
  `references/<source>/learn-more.md`, proportionate to the context. Do not lecture.

Learn more (verified pointers):

- Citation File Format - https://citation-file-format.github.io/
- CodeMeta terms - https://codemeta.github.io/terms/
- Semantic Versioning - https://semver.org/
- CRediT contributor roles - https://credit.niso.org/
- Zenodo GitHub integration -
  https://support.zenodo.org/help/en-gb/24-github-integration
- The Turing Way handbook - https://book.the-turing-way.org/
- CodeRefinery lessons - https://coderefinery.org/lessons/
- The Carpentries - https://carpentries.org/
- ELIXIR TeSS training portal - https://tess.elixir-europe.org/

---

Guidance based on [RSQKit](https://everse.software/RSQKit/) by the EVERSE
project and the RSQKit team, DOI
[10.5281/zenodo.14923573](https://doi.org/10.5281/zenodo.14923573)
(CC-BY-4.0).
