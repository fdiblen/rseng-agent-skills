<!-- Generated file - do not edit.
     Source: pages/tasks/releasing_software.md @ 03a8352e0701acf6ae28a1f6c9069e9b2caf8e7e
     From RSQKit (https://everse.software/RSQKit/releasing_software) by the EVERSE project and the RSQKit team,
     CC-BY-4.0. DOI: 10.5281/zenodo.14923573 -->

## How to Create Code Releases

### Description

A software release is the process of making a new or updated version of software available to users.
It's an important phase in software development cycle that involves several other stages, including: planning, development, testing, deployment, and maintenance.

### Considerations

* A software release is a new version of a software product, and a **release log** (changelog) is a document that records the changes
made to the software over time and is published with the software at the time of the release.
* **Software versioning** is the process of assigning either unique version names or unique version numbers to software releases.
Naming schemes can vary - for example [Semantic Versioning](https://semver.org/) (e.g. "1.0.2") and [Calendar Versioning](https://calver.org/) (e.g. "24.10").
* Attachments like built binaries or packages or other software artefacts can be provided with the release.

### Solutions

Code hosting and management platforms – like [GitHub](https://github.com/), [GitLab](https://about.gitlab.com/), and [BitBucket](https://bitbucket.org/) - offer features to help with releasing software automatically.

For example, to create a software release on GitHub:

- Go to your source code repository on GitHub.
- Prepare changelog ahead of the release process.
- Click on `Releases` and then on `Draft a new release` button.
- Decide on a software versioning scheme you will use and use a unique name or number for this release.
- Add release notes - a short and non overly technical summary of the changelog intended for end-users.
- Click on `Publish release`.
- If your repository is integrated with Zenodo - a new [DOI][software_identifiers] for this software release will automatically be issued by [Zenodo](https://zenodo.org/).

## Tool- or Domain-Specific Tasks

This is a suggested list tool-specific sub-tasks to have a look at.

[software_identifiers]: https://everse.software/RSQKit/software_identifiers
