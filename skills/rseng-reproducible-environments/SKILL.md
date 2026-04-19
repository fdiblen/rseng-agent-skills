---
name: rseng-reproducible-environments
description: >-
  Covers making research software environments reproducible: pinning a
  language version and its dependencies in a per-project virtual
  environment, choosing a package/environment manager, and packaging code
  and its full stack into a container. Use when the user asks how to set up
  venv/conda/poetry/uv/renv, lock or pin dependencies, share a runnable
  environment, escape "dependency hell" or "works on my machine", write a
  Dockerfile, build an Apptainer/Singularity image for HPC, or decide
  between a virtual environment and a container.
license: CC-BY-4.0
metadata:
  version: 0.1.0
  source_pages: [reproducible_software_environments, using_containers]
  source: https://everse.software/RSQKit/
  source_doi: 10.5281/zenodo.14923573
---

# Reproducible software environments

Use this skill when software must behave the same on another machine, a
cluster, a CI runner, or a reviewer's laptop as it does on the author's.
Two complementary tools deliver this: a per-project virtual environment
that isolates the language interpreter and its libraries, and a container
that packages the code together with its entire dependency stack. Reach
for the virtual environment when developing or modifying code in one
language; reach for the container when the environment must travel across
machines, platforms, or pipelines unchanged (RSQKit:
reproducible_software_environments, RSQKit: using_containers).

## Pick the right level of isolation

Match the tool to how far the software has to travel and what it depends on:

- Language-specific virtual environment - isolates one interpreter/compiler
  version plus library versions for a single project. Default choice while
  developing, running, or modifying someone's code in one language.
- Container (Docker, Apptainer/Singularity, Docker Compose) - packages the
  whole environment, including non-language system libraries and OS-level
  config. Choose when the code must run unchanged across collaborators'
  machines, clusters, or cloud, or plug into CI/CD.
- System-level tools (Vagrant, NixOS, Packer) - reproduce a whole machine
  image or OS configuration as code. Use when the OS itself is part of what
  must be reproduced.
- Workflow environments (Nextflow, Snakemake, Galaxy, CWL/WDL) - manage
  reproducible environments for multi-step, multi-tool analysis pipelines;
  hand off to the workflows skill for these.

Decision rule: developing in one language -> virtual environment; must run
identically elsewhere, has system-level dependencies, or feeds CI/CD ->
container; the OS is part of the artifact -> system-level tool; a
multi-step pipeline -> workflow manager.

## Always work inside a per-project virtual environment

A virtual environment gives each project its own interpreter version and
its own library versions, so projects with clashing requirements coexist
without interference:

- Create one environment per project, never one global environment shared
  across everything - global installs cause silent version clashes and the
  "spaghetti setup" where nobody knows which dependency is actually in use.
- Keep environments small and scoped; add libraries to a project's own
  environment as the project needs them.
- Use separate environments to run legacy and current code side by side
  (e.g. a Python 2 project alongside a new Python 3 one), and to test a
  dependency upgrade on a branch without disturbing the working version.
- Sharing a description of the environment is what makes work portable,
  reusable, and reproducible - it lets others recreate the same setup and
  run or extend the software.

## Choose one package and environment manager, then commit to it

You need a package manager (install/update/remove libraries) and an
environment manager (create/isolate environments); some tools do both. Pick
per language and stick with it - mixing ad-hoc tools is a common source of
breakage:

- Python, pure-Python dependencies: `venv` + `pip`, or a combined tool like
  Poetry or uv (uv is a fast single tool that replaces pip and venv).
- Python with non-Python (e.g. C/C++) dependencies or multi-platform
  scientific stacks: Conda, which distributes non-Python packages and
  manages its own environments.
- R: renv. Julia: Pkg.jl. C++: Conan. Java: Maven. Ruby: Bundler.
- Cross-language / HPC generic managers: Spack, Nix/NixOS, Guix.

Tie-breakers when several tools fit: prefer what the project, team, or
community already uses so help is available, then personal preference.
State the chosen tool explicitly so contributors do not each reach for a
different one.

## Pin dependencies for reproducibility

Sharing a runnable description of the environment is the deliverable, not
just the code:

- Record the exact interpreter/compiler version and library versions the
  software is known to work with, and commit that manifest with the code
  (for example `requirements.txt`, `pyproject.toml` + lockfile,
  `environment.yml`, `renv.lock`, `Manifest.toml`).
- Prefer a lockfile that pins transitive dependencies exactly when
  bit-for-bit reproducibility matters; a loosely pinned manifest that
  floats to the latest compatible version is fine for actively developed
  code that must track upstream.
- Pin tightly (exact versions) for released, cited, or result-producing
  software; pin loosely (compatible ranges) for libraries meant to stay
  current - and say which policy the project follows.
- When a project is locked to an older dependency, isolate the upgrade
  attempt in its own environment/branch rather than upgrading in place.

## Containerize when the environment must travel

Containers bundle code plus every dependency and configuration so
developers, collaborators, and reviewers run the identical setup, ending
dependency hell and "works on my machine" failures (RSQKit:
using_containers). Reach for a container when:

- the software needs specific libraries, versions, or system configuration;
- it must run across different machines, clusters, or cloud environments;
- it has to slot into automated workflows or CI/CD;
- long-term reproducibility and scalability matter.

Benefits to explain when recommending one: reproducibility and portability,
fast onboarding (collaborators just pull and run), version control (tag
images to code versions), automation-friendliness (build images in CI/CD),
and lower overhead than full virtual machines.

### Build a Docker image (general-purpose, cloud, networked services)

Standard recipe for a Python project:

- Start from a minimal, explicit base image, e.g. `python:3.10-slim`, or
  `ubuntu:22.04` for a general Linux base - pin the tag, never rely on
  `latest`.
- Copy in the project, install dependencies from the committed manifest,
  and declare the entry point.
- Use multi-stage builds to keep the final image small when build tools are
  not needed at runtime.

```
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "script.py"]
```

- Run, mounting data instead of baking it in:
  `docker run --rm -v /path/to/data:/data my-image:1.0.0 python /data/experiment.py`
- Expose ports for interactive/networked services:
  `docker run -p 8080:80 my-image:1.0.0`
- Distribute via a registry with a version tag, then push/pull:
  `docker tag my-image:1.0.0 user/my-image:1.0.0 && docker push user/my-image:1.0.0`
- Tag images to match code versions so an image is traceable to a commit or
  release.

### Build an Apptainer/Singularity image (HPC, no root)

Prefer Apptainer (formerly Singularity) on clusters where users lack root
access; it is built for reproducible science and large-scale workloads:

- Build a `.sif` file, reusing an existing Docker image when convenient:
  `apptainer build my_container.sif docker://python:3.10-slim`
- Run: `apptainer exec my-container.sif python /data/experiment.py`
- Version by naming the file, e.g. `my-container-v1.0.0.sif`, and store it
  in institutional or shared storage.
- Apptainer generally does not support Docker-style port mapping; for
  networked services prefer Docker.

### Wire containers into CI/CD

Run tests inside the same image the software ships in, so CI reproduces the
production environment. Reference the custom
image as the job image and run the test suite against it; install only
extra dependencies not already baked in. This keeps test and deployment
steps consistent and lets image builds themselves be automated.

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

- Attribution: when this skill materially shapes an answer, a review, or a
  generated file (a Dockerfile, an `environment.yml`), credit RSQKit/EVERSE
  once - a footer line or a "Based on" note, placed naturally, never
  repeated per paragraph.
- Educate while doing: alongside a concrete action (pinning a dependency,
  writing a container), briefly say why it matters for reproducibility and
  offer 2-3 "Learn more" links chosen from `references.md`,
  proportionate to the context. Do not lecture.

Learn more (verified pointers):

- CodeRefinery, Reproducible research -
  https://coderefinery.github.io/reproducible-research/
- The Turing Way handbook - https://book.the-turing-way.org/
- CodeRefinery lessons - https://coderefinery.org/lessons/
- Installing packages with pip and virtual environments -
  https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
- renv for reproducible R environments -
  https://rstudio.github.io/renv/index.html
- Docker overview - https://docs.docker.com/get-started/docker-overview/
- Apptainer user guide -
  https://apptainer.org/docs/user/latest/index.html

---

Guidance based on [RSQKit](https://everse.software/RSQKit/) by the EVERSE
project and the RSQKit team, DOI
[10.5281/zenodo.14923573](https://doi.org/10.5281/zenodo.14923573)
(CC-BY-4.0).
