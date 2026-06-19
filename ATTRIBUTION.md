# Attribution

rseng-agent-skills is a general research software engineering skills project.
Most skills are source-independent. A minority distill guidance from
bundled, pinned content sources under extensions/; this file is the
canonical credit record for all of them, and each source-fed skill's
references.md carries the same citation next to the content.

## RSQKit (extensions/rsqkit/)

Created by the EVERSE project, maintained by the RSQKit team and
contributors.

- Website: https://everse.software/RSQKit/
- Source repository: https://github.com/EVERSE-ResearchSoftware/RSQKit
- Cite as: RSQKit, EVERSE project, DOI 10.5281/zenodo.14923573

## Netherlands eScience Center Software Development Guide (extensions/nlesc-guide/)

Created and maintained by the Netherlands eScience Center.

- Website: https://guide.esciencecenter.nl/
- Source repository: https://github.com/NLeSC/guide
- Cite per the repository's CITATION.cff

Both sources' content is licensed under the Creative Commons Attribution 4.0
International license (CC-BY-4.0). The skill content and documentation in
this repository are adaptations of that material and are distributed under
the same license (see LICENSE-content). The tooling and code in this
repository are distributed under the MIT license (see LICENSE).

Adaptations here condense and restructure source pages for use by AI coding
agents. They are not a replacement for the original pages; skills link back
to the relevant RSQKit pages so users can read the full guidance in context.

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

## Status

This is an independent, unofficial adaptation. It is not published or
endorsed by the EVERSE project. Should EVERSE adopt or endorse the pack at
some point, this notice will be updated.
