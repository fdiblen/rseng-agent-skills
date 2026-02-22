---
name: rseng-testing
description: >-
  Covers how to test research software: choosing test types and levels
  (unit, integration, system, regression), applying test frameworks and
  coverage, and taming large CI testing matrices across compilers,
  platforms, and dependency versions. Use when the user asks how to write
  tests, set up pytest/testthat/JUnit, decide what to test, raise or
  interpret code coverage, do test-driven development, or when a CI matrix
  is exploding across compiler, OS, or library-version combinations.
license: CC-BY-4.0
metadata:
  version: 0.1.0
  source_pages: [testing_software, ci_testing_matrices]
  source: https://everse.software/RSQKit/
  source_doi: 10.5281/zenodo.14923573
---

# Testing research software

Use this skill when writing tests for research code, setting up a test
framework, deciding what and how much to test, or designing a CI test
matrix that has grown across compilers, platforms, and dependency
versions. The goal is code whose results others can trust and reproduce,
so favour tests that are automated, saved with the code, and run on every
change (RSQKit: testing_software).

## Decide what kind of tests to write

Always start with functional testing, then add non-functional testing only
where a requirement demands it (RSQKit: testing_software).

- Functional testing - does the software produce correct outputs for given
  inputs? Pick the level by scope:
  - Unit tests: one small unit of functionality (a single function/method)
    in isolation. This is the minimum bar for any research code.
  - Integration tests: multiple modules/components working together along a
    functional path.
  - System / end-to-end tests: the whole application behaving correctly
    against its requirements.
  - Regression tests: outputs have not changed after a code change; run
    them after every bug fix or new feature.
  - User acceptance tests: real user/business needs are met.
- Non-functional testing - add when the requirement exists, not by default:
  - Performance/load, usability, security, compatibility (browsers, OSes,
    devices), and compliance-with-standards tests.
- Decision rule: unit tests always; integration/system tests once
  components interact; regression tests whenever behaviour must stay
  stable; non-functional tests keyed to explicit requirements (many users
  -> performance; multiple platforms -> compatibility) (RSQKit:
  testing_software).

Tactics to choose between: black-box (test behaviour without knowing
internals) versus white-box (test specific internal paths and conditions).

## Write good tests (F.I.R.S.T.)

Apply these properties to every test (RSQKit: testing_software):

- Fast: run quickly so feedback is immediate.
- Isolated/Independent: each test checks one responsibility and does not
  depend on the state or ordering of other tests.
- Repeatable: deterministic; same input gives same result regardless of
  environment.
- Self-validating: automated pass/fail, no manual inspection of output.
- Thorough/Timely: cover edge cases and error paths (not just happy
  paths), and write tests at the right time - ideally test-first.

Additional checklist when authoring or reviewing a test:

- Give the test a descriptive name that states what it verifies.
- Verify one condition per test.
- Use inputs whose correct output you already know.
- Keep tests in a dedicated `tests/` folder, version-controlled and shipped
  with the code.
- Do no harm: tests belong in the test environment, never wired into
  production.

## Test-driven development

Consider a test-first policy: write the failing test just before the code
that makes it pass. This forces small, testable units from the start
instead of refactoring for testability later (RSQKit: testing_software).

## Principles to keep expectations honest

State these when advising, so nobody over-trusts a green test suite
(RSQKit: testing_software):

- Testing shows the presence of defects, never their absence.
- Exhaustive testing is impossible - prioritise instead of chasing every
  path.
- Test early and often for rapid feedback.
- Defects cluster: found one in a unit, look for more there.
- Pesticide paradox: re-running identical tests finds nothing new; add new
  cases to find new defects.
- Testing is context-dependent: match the approach to the software type.

## Coverage guidance

- Aim for high coverage to shrink the space of undetected bugs, but do not
  treat 100% as the goal (RSQKit: testing_software).
- 100% coverage does not mean bug-free.
- Skip testing well-tested third-party/library code and language built-ins.
- Prioritise critical paths, complex logic, edge cases, and any code that
  carries "reputational risk" - i.e. could distort reported results.
- Keep a balance: automate the repeatable checks, reserve manual testing
  for exploratory and usability work where human judgement matters.

## Automate with a test framework, then CI

Progress from informal manual checks (fine for first drafts, but forgotten
once the editor closes) to saved test functions, to a full framework
(RSQKit: testing_software):

- Pick the framework for the language: pytest (Python), testthat (R), JUnit
  (Java), the Test standard library (Julia).
- Frameworks auto-discover tests by naming convention (files/functions
  named `test_*` or `*_test`), run them, compare actual vs expected, and
  emit a report.
- Wire the framework into Continuous Integration so tests run
  automatically on every push/merge on an integration machine (e.g. GitHub
  Actions, GitLab CI/CD), not just on demand locally (RSQKit:
  testing_software).
- Automated + CI testing buys wider coverage, earlier error detection,
  lower maintenance, and consistent runs across environments and
  platforms.

## Manage large CI testing matrices

When research software must support many compilers, library versions,
architectures, and runtimes, a naive full matrix explodes - e.g. 4 GCC x
6 Clang x 10 CUDA x 4 CMake x 7 Boost = 2,800 jobs (~9.3 h even with 30
parallel runners). Use these strategies (RSQKit: ci_testing_matrices):

- Prefer pairwise testing over the full matrix. Ensuring every pair of
  parameter values appears in at least one job cuts ~2,800 combinations to
  ~60-100 jobs (~20-30 min) while keeping all 2-way interaction coverage.
  Generate jobs with a library such as `allpairspy`; random sampling
  (~200 jobs) is a weaker fallback.
- Encode exclusion rules to drop known-incompatible combinations (e.g. an
  old CUDA with a new GCC, or CUDA on PowerPC) instead of testing them.
- Generate the matrix dynamically. Use GitLab dynamic child pipelines or
  GitHub Actions matrix strategies so the job set is computed at runtime
  from available resources.
- Speed up builds with containers: pre-built images with compiled
  dependencies, multi-stage builds, layer caching, and a registry close to
  the runners.
- Use wave scheduling: run fast/critical checks in an early stage, then
  medium combinations, then the full slow GPU/HPC matrix. This fails early
  and frees shared infrastructure between waves.
- Allow selective testing during development (e.g. commit-message tags like
  `[cuda-only]`) so iterative work does not trigger the whole pipeline.
- Add performance-regression jobs with baselines and thresholds where
  performance is a requirement, not just correctness.
- Monitor pipeline health (job duration, queue time, failure rate,
  utilisation) and prune the matrix as versions age.

Rollout when adopting this: catalog every parameter dimension, start with
pairwise core-compatibility testing, add specialized hardware incrementally,
then performance testing, then full multi-platform validation. Document why
each parameter and exclusion exists (RSQKit: ci_testing_matrices).

- Sustainability note: extensive matrices consume real energy. Run the full
  matrix only when it earns its cost (e.g. before releases) and use smaller
  subsets for day-to-day development (RSQKit: ci_testing_matrices).

## Working with this skill

The pipeline-generated `references/` folder beside this file holds the
source material and pointers:

- `references/pages/testing_software.md` and
  `references/pages/ci_testing_matrices.md` - cleaned upstream fragments
  with the full detail behind the checklists above.
- `references/indicators.md` - the quality-indicator checklist for testing.
- `references/learn-more.md` - the verified external links.

Consult the page fragments when a user needs the reasoning or examples
(e.g. the `allpairspy` snippet or GitLab wave-scheduling YAML) rather than
just the rule.

## Attribution and teaching

- Attribution: when this skill materially shapes an answer, review, or a
  generated file, credit RSQKit/EVERSE once - a footer line or a "Based on"
  note, placed naturally, never repeated per paragraph.
- Educate while doing: alongside a concrete action (adding a test,
  proposing a matrix), briefly say why it matters and offer 2-3 "Learn
  more" links chosen from `references/learn-more.md`, proportionate to the
  context. Do not lecture.

Learn more (verified pointers):

- CodeRefinery, Software testing - https://coderefinery.github.io/testing/
- The Turing Way handbook - https://book.the-turing-way.org/
- CodeRefinery lessons - https://coderefinery.org/lessons/
- pytest documentation - https://docs.pytest.org/en/stable/
- testthat (R) - https://testthat.r-lib.org/
- Test patterns (xUnit Patterns) - http://xunitpatterns.com/
- Pairwise testing with allpairspy -
  https://pypi.org/project/allpairspy/
- Alpaka job matrix library -
  https://github.com/alpaka-group/alpaka-job-matrix-library
- GitLab dynamic child pipelines -
  https://docs.gitlab.com/ee/ci/pipelines/downstream_pipelines.html#dynamic-child-pipelines
- Docker multi-stage builds -
  https://docs.docker.com/build/building/multi-stage/

---

Guidance based on [RSQKit](https://everse.software/RSQKit/) by the EVERSE
project and the RSQKit team, DOI
[10.5281/zenodo.14923573](https://doi.org/10.5281/zenodo.14923573)
(CC-BY-4.0).
