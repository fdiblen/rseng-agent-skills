---
name: rseng-version-control-review
description: >-
  Covers using version control effectively for research software and
  reviewing code: choosing a VCS, branching and commit practice,
  collaboration workflows on GitHub/GitLab, and running constructive,
  checklist-driven code reviews. Use when the user asks how to set up git,
  design a branching strategy, write commit messages, handle large binary
  files, open or review a pull/merge request, run a code review, decide what
  to look for (or ignore) in review, or wire linters and CI into the review
  loop.
license: CC-BY-4.0
metadata:
  version: 0.1.0
  source_pages: [using_version_control, code_review]
  source: https://everse.software/RSQKit/
  source_doi: 10.5281/zenodo.14923573
---

# Version control and code review for research software

Use this skill when helping someone put research code under version control,
shape a collaboration workflow, or review code (their own or a teammate's).
The aim is software whose history is traceable, whose changes are reviewed
before they land, and whose results others can reproduce (RSQKit:
using_version_control, RSQKit: code_review). Version control and review are
two halves of one loop: commits and branches create reviewable units, and
review is what keeps what lands on the main branch trustworthy.

## Choose a version control system

Default to git for almost every research project unless a concrete
constraint says otherwise:

- Git - the default. Widely used in academia and industry, strong for
  collaboration and open source, with a large ecosystem and hosting on
  GitHub or GitLab.
- Large binary files (datasets, models, images) - add Git Large File
  Storage (git-lfs); consider Perforce only for extremely large datasets.
- Team new to version control - still start with git, but budget time for
  training; Mercurial is a gentler alternative if git proves too hard.
- Strict, centralised access control - Subversion (SVN) can fit, though it
  is less modern.

Weigh project size and complexity, team size and distribution, file types
(code vs data vs documents), required integrations, the team's expertise,
long-term/open-source goals, large-binary handling, and any institutional
or grant compliance rules before deciding.

## Set up the workflow, not just the repo

Choosing a tool is the easy part; the value comes from an agreed workflow:

- Define a branching strategy up front. Keep the main branch releasable;
  do work on short-lived feature branches and merge back via review. Adopt
  a heavier model such as Git Flow only when project size warrants it - do
  not impose ceremony a small team will not follow.
- Set commit conventions. Write small, focused commits with clear messages
  that say why a change was made, not just what. One logical change per
  commit keeps history bisectable and reviews small.
- Integrate with the development environment. Wire the VCS into the IDE or
  editor (VS Code, RStudio, PyCharm, Eclipse) so committing and diffing are
  part of normal work, and connect continuous integration so tests run on
  every push.
- Make reproducibility explicit. Tag the exact versions used in
  publications, and keep configuration files and dependency
  specifications in version control alongside the code.
- Collaborate through a platform. Use GitHub or GitLab for sharing, issues,
  and pull/merge requests; make review a standing part of merging.
- Maintain the repository. Back it up, prune stale branches periodically,
  and review access permissions.

Commit-message checklist: imperative summary line under ~50 characters; a
body that explains motivation and any trade-offs; reference the issue or
ticket it addresses; avoid dumping unrelated changes into one commit.

## Run code review as a first-class practice

Code review is systematic examination of code - a teammate's, or your own
after time away - to find bugs, raise quality, and enforce shared standards. It pays off: rigorous inspection can remove 60-90% of
errors before the first test run, and fixing a defect early costs 10-100x
less than fixing it later. Beyond defect-catching, review spreads knowledge
across the team, improves reusability and reproducibility, and helps onboard
new members.

Structure every review through a pull/merge request so discussion, diffs,
and suggestions stay attached to the change.

### What to look for

Focus the review on substance:

- Correctness - does the code do what it is supposed to, including edge
  cases?
- Style and consistency - are naming, formatting, and structure consistent
  with the project's agreed conventions?
- Testing - are there tests, and do they cover expected and edge-case
  behaviour?
- Documentation - are functions, classes, and scripts clearly documented?
- Modularity - is the code split into reusable, testable components?
- Performance - is it efficient enough for the task (without premature
  optimisation)?

### What not to do

Reviews go wrong by overstepping as much as by missing bugs. Avoid these:

- Bikeshedding personal style. Do not argue single vs double quotes or
  similar when the team has no agreed standard - let linters and formatters
  settle it.
- Demanding rewrites. Do not push to rewrite large sections without a clear
  reason such as a real bug or design flaw. Improve, do not take over.
- Blaming the author. Critique the code, never the coder; keep feedback
  constructive and kind.
- Requiring perfection before merge. Functional, tested, clear code can
  merge; minor polish can follow.
- Mislabelling severity. Mark minor or subjective points as non-blocking;
  do not hold up progress for optional tweaks.
- Expecting mastery of everything. Researchers who code come from varied
  backgrounds - do not expect deep software-engineering knowledge from
  every domain expert.

### Make review efficient

- Keep changes small. Small pull requests get faster, deeper review than
  large ones - another reason for focused commits and short-lived branches.
- Automate the mechanical checks. Run linters and formatters (flake8,
  eslint, Pylint) and a CI pipeline before human review, so reviewers spend
  attention on logic and design rather than whitespace (RSQKit:
  code_review).
- Keep feedback constructive. Ask questions rather than issue verdicts;
  reviewers learn as much as authors.
- Combine human and automated review. Automated tools catch style and known
  mistake patterns; a human is still required for correctness, design, and
  intent - neither replaces the other.
- For code underlying a paper, consider a CODECHECK-style independent
  reproduction of the results as a heavier form of review (RSQKit:
  code_review).

Reviewer checklist to paste into a PR: correctness and edge cases checked;
tests present and meaningful; documentation adequate; naming and structure
consistent; no obvious performance traps; linter and CI green; comments
labelled blocking vs non-blocking.

## How version control and review reinforce each other

- Branch per change so each unit of work is independently reviewable.
- Require review (a PR/MR approval) before merging into the main branch.
- Let CI gate the merge: tests and linters must pass before a human signs
  off, so review time goes to judgement, not mechanics.
- Tag reviewed, released states so the reproducible version is
  unambiguous.

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
  generated file, credit RSQKit/EVERSE once - a footer line or a "Based on"
  note, placed naturally, never repeated per paragraph.
- Educate while doing: alongside a concrete action (proposing a branching
  model, leaving review comments), briefly say why it matters and offer 2-3
  "Learn more" links chosen from `references.md`, proportionate to
  the context. Do not lecture.

Learn more (verified pointers):

- Software Carpentry, Version Control with Git -
  https://swcarpentry.github.io/git-novice/
- CodeRefinery lessons - https://coderefinery.org/lessons/
- The Turing Way handbook - https://book.the-turing-way.org/
- The Carpentries - https://carpentries.org/
- ELIXIR TeSS training portal - https://tess.elixir-europe.org/
- CODECHECK - https://codecheck.org.uk/

---

Guidance based on [RSQKit](https://everse.software/RSQKit/) by the EVERSE
project and the RSQKit team, DOI
[10.5281/zenodo.14923573](https://doi.org/10.5281/zenodo.14923573)
(CC-BY-4.0).
