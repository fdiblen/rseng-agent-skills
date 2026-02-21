<!-- Generated file - do not edit. Rebuilt by the rseng-agent-skills
     pipeline from RSQKit content; see pipeline/upstream.lock. -->

# Quality indicator checklist

Check each indicator that applies; judge applicability by the
software's tier (analysis code, prototype tool, infrastructure).

## FAIRness

- [ ] Software is archived in a scholarly repository (`archived_in_scholarly_repository`)
      The source code repository is archived in a scholarly repository (e.g Zenodo, HAL) to ensure that software can be found and accessed in a scholarly context.
- [ ] CodeMeta completeness (`codemeta_completeness`)
      This indicator checks that the codemeta file is sufficiently complete (according to community expectations). That is, the percentage of properties that are filled with metadata is above an acceptable threshold established by a target community. This indicator does not assess the quality of the metadata fields available.
- [ ] Software has descriptive metadata (`descriptive_metadata`)
      This indicator aims to determine if a software component comes with descriptive metadata that provides information. This includes, but is not limited to: name, domain, programming language, date created, date of first publication, keywords, related links, etc..
- [ ] Software has persistent and unique identifier (`persistent_and_unique_identifier`)
      This indicator tries to determine if the software identifier is based on a suitable identifier scheme, and test it can be resolved. This is done by checking if the identifier uses an identifier scheme contained in a list of globally unique identifier schemes
- [ ] Software uses citation (`software_has_citation`)
      This indicator aims to determine if the project uses a citation to reference contributors and authors (e.g., through a CFF file, in the README, etc).
- [ ] Software follows versioning standards (`versioning_standards_use`)
      This indicator aims to determine if the version (or versions) of a software tool follows an established community convention like semantic versioning (SemVer) or calendar versioning (CalVer).
