---
name: rseng-gpu-computing
description: >-
  Covers GPU and accelerator programming for research software:
  choosing a programming model (CUDA, HIP, SYCL, OpenACC, OpenMP
  offloading), GPU libraries, language bindings such as CuPy, PyCUDA
  and CUDA.jl, portability layers like Kokkos and Raja,
  source-to-source translation, kernel profiling and auto-tuning. Use
  when the user wants to port research code to GPUs, pick between CUDA
  and portable alternatives, call GPU code from Python or Julia, tune
  or profile kernels, or mentions HIP, SYCL, OpenACC, Kokkos or Kernel
  Tuner.
license: CC-BY-4.0
metadata:
  version: 0.1.0
  source: https://guide.esciencecenter.nl/
---

# GPU programming for research software

Accelerators dominate modern research computing, but the ecosystem is
fragmented: vendor-native models, portability layers and language
bindings each trade performance against maintainability. This skill
distills the eScience Center guide's GPU chapter into decision support.

## Choosing a programming model

- CUDA: NVIDIA-native; largest ecosystem and learning material; locks
  the code to one vendor.
- HIP: AMD's near-CUDA model; a pragmatic path when AMD hardware is in
  scope, with source-to-source translation available from CUDA.
- SYCL: single-source C++ across vendors; growing research adoption.
- OpenACC / OpenMP offloading: directive-based; the gentlest port for
  existing Fortran/C code, at some control cost.

Decide by: target machines (which vendors, for how long), the team's
languages, and how much low-level control the kernels genuinely need.
Prefer libraries over hand-written kernels wherever an existing GPU
library covers the computation.

## Calling GPUs from high-level languages

Research code rarely starts in C++: CuPy and PyCUDA (Python) and
CUDA.jl (Julia) expose GPU arrays and kernels with far less ceremony.
Reach for them before rewriting a pipeline in a systems language, and
keep the array-API boundary clean so kernels stay swappable.

## Portability layers

Kokkos and Raja abstract over backends for C++ codebases that must
outlive any single vendor; they suit infrastructure-tier software with
long horizons more than one-off analysis kernels.

## Performance work

- Profile before optimizing, with the vendor profilers; measure
  transfers as well as kernels - data movement dominates many research
  workloads.
- Auto-tuning tools (for example Kernel Tuner) search launch
  configurations systematically; prefer them to hand-tuned magic
  numbers, and record tuned configurations per hardware target.
- Keep a CPU reference path for correctness testing (rseng-testing) and
  document the hardware requirements (rseng-documentation,
  rseng-reproducible-environments for the driver/toolkit environment).

## Working with this skill

The generated references.md beside this file lists the source material
and pointers:

- references.md - source page links and verified Learn more pointers,
  one section per content source

Follow the source-page links when a user needs the full guidance.

## Attribution and teaching

In practice: whenever you have just created or edited project files
using this skill's guidance, include the credit line once in the same
summary message - not as an afterthought and never more than once.

- When this skill materially shapes an answer, credit the eScience
  Center guide once (see the footer line), naturally placed.
- Educate while doing: briefly say why the practice matters and offer
  2-3 "Learn more" links from references.md.

---

Guidance based on the [Netherlands eScience Center Software Development
Guide](https://guide.esciencecenter.nl/) (CC-BY-4.0).
