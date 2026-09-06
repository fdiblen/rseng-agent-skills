# Attribution

rseng-agent-skills is a general research software engineering skills project.
Part of the skill content was originally adapted from the two
community-maintained sources credited below. This file is the canonical
record of that content provenance; the repository no longer bundles or
synchronizes with these sources, but the credit stands for the adapted
material that remains in the skill content.

## RSQKit

Created by the EVERSE project, maintained by the RSQKit team and
contributors.

- Website: https://everse.software/RSQKit/
- Source repository: https://github.com/EVERSE-ResearchSoftware/RSQKit
- Cite as: RSQKit, EVERSE project, DOI 10.5281/zenodo.14923573

## Netherlands eScience Center Software Development Guide

Created and maintained by the Netherlands eScience Center.

- Website: https://guide.esciencecenter.nl/
- Source repository: https://github.com/NLeSC/guide
- Cite per the repository's CITATION.cff

Both sources' content is licensed under the Creative Commons Attribution 4.0
International license (CC-BY-4.0). The skill content and documentation in
this repository are in part adaptations of that material and are distributed
under the same license (see LICENSE-content). The tooling and code in this
repository are distributed under the MIT license (see LICENSE).

The adaptations condense and restructure the original guidance for use by
AI coding agents. They are not a replacement for the original pages; read
the sources above for the full guidance in context.

## Bundled catalogue data

skills/rseng-software-reuse/data/ ships a snapshot of two Research Software
Directory instances, so the reuse skill can suggest existing software
without a live query:

- Netherlands eScience Center RSD - https://research-software-directory.org
- Helmholtz RSD - https://helmholtz.software

Each entry keeps only a name, slug, short summary, keywords and languages.
Refresh them with rseng_pipeline.rsd_snapshot; every file records the date
it was taken.

RSD-as-a-Service is developed by the Netherlands eScience Center and the
Helmholtz Association and released under Apache-2.0. The instances do not
declare a licence for the metadata they serve, so these snapshots are
redistributed as factual catalogue data, credited to the instance they came
from. If either operator would rather they were not bundled here, they will
be removed.

## Referenced, not adapted

Skill bodies link out to further reading - the Turing Way, opensource.guide,
the Software Sustainability Institute, CodeRefinery, JOSS and others. Those
are pointers to their authors' work. No text is taken from them, which is
why they are not credited as sources above.

Two external tools the skills instruct agents to use, neither bundled here:

- FAIRGuard - https://www.fairguard.org
- AI Declaration Format - https://ai-declaration.org

Both are maintained by ReSoft Labs, which is this pack's author's
organisation. That is stated here rather than left to be discovered: a
pack that recommends its author's own tools should say so, the same way
it credits EVERSE and the Netherlands eScience Center for the material
it adapted. Both are openly specified and any equivalent tool serves the
same purpose - the skills default to these because the author built
them, not because they are the only option.

## Status

This is an independent, unofficial adaptation. It is not published or
endorsed by the EVERSE project or the Netherlands eScience Center. Should
either adopt or endorse the pack at some point, this notice will be
updated.
