<!-- Generated file - do not edit.
     Source: pages/tasks/archiving_software.md @ 03a8352e0701acf6ae28a1f6c9069e9b2caf8e7e
     From RSQKit (https://everse.software/RSQKit/archiving_software) by the EVERSE project and the RSQKit team,
     CC-BY-4.0. DOI: 10.5281/zenodo.14923573 -->

## How to ensuring long-term reproducibility and access to research software?

In research domains that rely heavily on computation, software is not just a tool — it is an integral part of the scientific process.
However, software is inherently fragile: it evolves rapidly, becomes deprecated, and often depends on specific environments, libraries, or hardware.
As a result, many research outputs become irreproducible or unusable within just a few years due to the lack of access to the original software environment.
Without systematic software archiving, research risks losing critical components of its provenance, making long-term validation, replication, and reuse of results impossible.

Putting code on [GitHub](https://github.com/) or [GitLab](https://about.gitlab.com/) (or any similar code hosting service) is good practice for code sharing, versioning and even code packaging, it is not enough for long-term software archiving.
This is because these are commercial services - if they change their policies, remove repositories (e.g. for inactivity, or security reasons), or even shut down (which has happened to code sharing platforms in the past), your code could disappear.

Archival means long-term preservation independent of any one platform.

### Benefits for research communities

Implementing proper software archiving practices brings significant value:

- Reproducibility - future researchers can rerun computational experiments with the exact same software stack.
- Preservation of scientific value - the loss of valuable tools, simulations or models that underpin published work is prevented.
- Compliance with Open Science mandates - meeting funder and journal requirements for software availability and preservation.
- Collaboration and reuse - archived software can be rediscovered, cited, and reused by other researchers, accelerating innovation.

### Considerations

Effective software archiving in research is more complex than simply saving source code.
It requires addressing multiple interrelated technical aspects:

- Environment preservation - dependencies on compilers, libraries (e.g., NumPy, R packages), OS-level features, and system architectures must be captured.
- Build reproducibility - binary reproducibility is often non-trivial due to non-deterministic build processes or missing historical dependencies.
- Versioning and provenance - capturing software version history, commit hashes, and linkages to specific datasets or publications is essential.
- Emulation and virtualisation - for legacy software, virtual machines or emulators may be necessary to recreate the execution environment.
- [Licensing][licensing_software] constraints - proprietary software dependencies can limit what can legally be archived and shared.
- [Metadata][software_metadata] and [documentation][documenting_software] - proper archival demands machine- and human-readable metadata, including usage instructions, authorship, and configuration settings.

### Archival solutions for research software

Several archival solutions for research software are emerging:

- [Software Heritage](https://www.softwareheritage.org) can provide an universal archive of source code, capturing the development history of open-source software at scale.
- [ReproZip](https://www.reprozip.org/) captures the execution environment of research software, enabling portability and reproducibility across platforms.
- [Guix](https://guix.gnu.org/) / [NixOS](https://nixos.org/) are functional package managers that enable reproducible builds and isolated software environments.
- Containers (e.g., [Docker](https://www.docker.com/), [SingularityCE](https://sylabs.io/singularity/)) are popular tools for bundling applications with dependencies, especially in high-performance computing.
- VM snapshots are used when containerisation is not feasible, particularly for GUI-based or legacy software.
- Institutional repositories and [Zenodo](https://zenodo.org/) provide [DOI-backed software][software_identifiers] archiving linked to publications, ensuring persistent citation and access.
- [RO-Crate](https://www.researchobject.org/ro-crate/) has an honourable mention here, while it is not an archival mechanism it is a critical metadata format that ensures items (e.g., [workflows](https://everse.software/RSQKit/computational_workflows)) that are archived are described, understandable and reusable.

### Conclusion

Software archiving is now a foundational component of digital research infrastructure.
As the scientific community moves toward open, reproducible, and [FAIR (Findable, Accessible, Interoperable, Reusable) principles][fair_rs], robust software preservation practices are essential.
Researchers must adopt workflows and tools that not only produce results but also ensure those results can be trusted and reused decades from now.

## Tool- or Domain-Specific Tasks

This is a suggested list tool-specific sub-tasks to have a look at.

[fair_rs]: https://everse.software/RSQKit/fair_rs
[software_metadata]: https://everse.software/RSQKit/software_metadata
[documenting_software]: https://everse.software/RSQKit/software_documentation
[software_identifiers]: https://everse.software/RSQKit/software_identifiers
[licensing_software]: https://everse.software/RSQKit/licensing_software
