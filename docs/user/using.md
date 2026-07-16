# Using the skills

Once the pack is installed, you do not call the skills by name. You work
normally, describing what you want in plain language, and the agent pulls in
the matching skill when your request lines up with what that skill covers.
Each skill's frontmatter lists the triggers ("Use when the user asks
how to..."), and the agent matches against them.

This page shows what that feels like in practice: a handful of skills with a
realistic prompt and what the skill adds, the fourteen Claude Code slash
commands, the six subagents, and the behaviour you will notice in
every response - the "Learn more" links.

## How a skill changes an answer

Without the pack, an agent answers research-software questions from generic
training. With the pack, answers follow the skills' curated practice
guidance - distilled research software engineering practice with
verified "Learn more" links, so you can read the material any
recommendation rests on. The examples below use Claude Code phrasing,
but the skills behave the same in any agent the pack supports.

### Testing (rseng-testing)

Prompt you might type:

```
Help me add tests to this data-analysis script. Where do I even start?
```

What the skill contributes: it steers you to functional testing first (unit
tests as the minimum bar, then integration and system tests once components
interact), applies the F.I.R.S.T. properties (Fast, Isolated, Repeatable,
Self-validating, Thorough/Timely) to each test, and keeps expectations
honest with principles like "testing shows the presence of defects, never
their absence." If your CI matrix has grown across compilers, OSes and
dependency versions, it also covers how to tame that.

### Citation metadata (rseng-citation-metadata)

Prompt:

```
Make this repository citable.
```

What the skill contributes: field-by-field guidance for a `CITATION.cff`
and a `codemeta.json`, how to mint persistent identifiers (DOIs via Zenodo,
ORCIDs for authors), and how to record credit (CRediT roles). It insists on
deriving metadata from real sources - git history, existing package
metadata - rather than inventing authors or DOIs.

### Licensing (rseng-licensing)

Prompt:

```
Which open source license should I use, and is it compatible with my
GPL dependency?
```

What the skill contributes: the difference between permissive, copyleft and
Creative Commons licenses, how to check compatibility with your
dependencies, and how to add the license concretely - a `LICENSE` file plus
per-file SPDX identifiers following REUSE, including how to license docs and
data alongside code.

### CI/CD (rseng-ci-cd)

Prompt:

```
Set up CI so my tests run on every pull request.
```

What the skill contributes: CI/CD concepts for research software and
concrete pipelines for GitHub Actions or GitLab CI/CD. It also covers the
less common cases - self-hosted or GPU runners, mirroring a repository, and
wiring an organisation's GitLab CI to a GitHub-hosted project while
reporting status back to GitHub.

### Reproducible environments (rseng-reproducible-environments)

Prompt:

```
"Works on my machine" - how do I make this environment reproducible for
my collaborators?
```

What the skill contributes: pinning a language version and dependencies in a
per-project environment (venv, conda, poetry, uv, renv), when to lock
versions, and when to escalate from a virtual environment to a container
(Dockerfile, or Apptainer/Singularity for HPC).

The other skills in the pack - documentation, FAIR software, publishing and
releasing, code quality, version control and review, maintenance and
sustainability, management and planning, workflows, and the overall quality
framework - trigger the same way when your request matches them.

## Slash commands

The plugin adds fourteen commands for tasks you want to run deliberately
rather than wait for a skill to trigger. Each inspects your repository
read-first and produces a concrete artifact. Besides Claude Code, the
commands ship translated for Gemini CLI (TOML custom commands), GitHub
Copilot (`.github/prompts/*.prompt.md` prompt files) and Cursor
(`.cursor/commands/*.md`). The full set:

- `/rseng-check` - assess the repository against research software
  engineering practice.
- `/rseng-cite` - generate or update `CITATION.cff` and `codemeta.json`.
- `/rseng-plan` - draft a Software Management Plan skeleton.
- `/rseng-release` - run the pre-release checklist and prepare the release.
- `/rseng-reproduce` - clean-room reproduction check of the repository.
- `/rseng-deps` - audit every dependency on all six vetting axes.
- `/rseng-integrity` - pre-submission integrity battery for manuscript and
  results.
- `/rseng-declare` - create or update the `aidecl.yaml` AI usage declaration.
- `/rseng-metrics` - code and community health metrics snapshot.
- `/rseng-digest` - draft the high-level project log digest for the period.
- `/rseng-lesson` - record a lesson learned and draft its prevention
  artifact.
- `/rseng-onboard` - generate a project-specific onboarding checklist.
- `/rseng-kickoff` - interview-driven setup of a new research software
  project.
- `/rseng-panel` - convene a panel of role-scoped expert subagents on a
  question (Claude Code only).

On agents without a hook system (Codex, Gemini, Copilot, Cursor) the
install also ships `rseng-check/rseng_check.py`, a dependency-free
self-check the agent is instructed to run before finishing any coding
task: it audits the practice artifact floor (README, LICENSE,
aidecl.yaml, CITATION.cff, tests, environment declaration) and the
phased practice worklog, mirroring what Claude Code enforces through
hooks.

The three commands below are described in more detail because they are the
ones you will likely reach for first; the others follow the same pattern
and name the skill they follow in their command file.

### /rseng-check

```
/rseng-check
```

Assesses the current repository against the pack's quality indicator
checklists. It first infers the software tier - analysis code, prototype
tool, or research software infrastructure - because that calibrates every
judgement, then reports one line per indicator (met / partial / missing /
not applicable) with the evidence found or its absence. It ends with the
top three next steps, each naming the sibling skill that covers it. It is
read-only; it does not modify your repository. You can pass arguments to
limit the assessment to specific quality dimensions or indicator ids.

### /rseng-cite

```
/rseng-cite
```

Generates or updates `CITATION.cff` and `codemeta.json`. It gathers facts
before writing - authors from `git shortlog -sne`, title and license from
the README and packaging metadata, version and date from the latest tag -
and asks you when author identity, ORCIDs or affiliations are ambiguous. It
never fabricates DOIs. If the files already exist, it updates them in place
and shows a diff-style summary of what changed and why.

### /rseng-plan

```
/rseng-plan
```

Drafts a Software Management Plan (`SMP.md`) skeleton at the repository root.
It matches the plan's depth to the software tier - a page or two for
analysis code, a few pages for infrastructure - prefills each section with
what the repository already shows, and marks genuinely open decisions with
`[DECIDE: ...]` placeholders naming who should decide, rather than inventing
policies or funders.

## The subagents (Claude Code)

The plugin installs six subagents. Each runs in its own context, so a
long audit or review does not crowd out your main session:

- `rseng-auditor` - read-only quality auditor; severity-rated findings
  before a release or publication.
- `rseng-reviewer` - codebase reviewer that fixes what it finds: ranked
  findings first, implementation only after you agree.
- `rseng-librarian` - read-only citation and claim verifier for
  references, bibliographies and `CITATION.cff` entries.
- `rseng-scout` - read-only reuse and dependency scout; searches research
  software directories and vets candidates before you build or adopt.
- `rseng-compliance-officer` - read-only regulatory and license compliance
  sweep (GDPR code-shaped obligations, EU AI Act positioning, dependency
  licenses).
- `rseng-mentor` - teaching-focused mentor for learning a practice on your
  real project rather than having it done for you.

The auditor is the one you will likely use first. Invoke it when you want
a quality audit of a repository - for example before a release or a
publication:

```
Use the rseng-auditor subagent to audit this repository before release.
```

It classifies the software tier first, works through the same
indicator checklist, and verifies claims rather than trusting file names (a
`tests/` directory with no runnable tests is a finding; a badge with no
backing workflow is a finding). It reports severity-rated findings -
CRITICAL, MAJOR, MINOR, INFO - most severe first, each with the indicator
id, the evidence, and one concrete remediation step. It is strictly
read-only: it audits, it never modifies files.

The difference from `/rseng-check`: the command is a quick indicator
sweep; the subagent runs a fuller, severity-rated audit in its own context.

## Content credits

The pack does not inject credit or citation lines into the agent's
output. Part of the skill content was originally adapted from
community-maintained material published under CC-BY-4.0; the
repository's ATTRIBUTION.md is the canonical record of that content
provenance.

## Educate while doing

The skills are built to teach, not just to act. When a command or a
subagent points you at a next step, it offers a "Learn more" link drawn
only from that skill's curated reference list (each skill's
`references.md`) - vetted training material and reference pages behind
the topic, not arbitrary search results. Following one takes you to a
source the guidance actually rests on, so an answer is a starting point
for understanding a practice, not just an instruction to follow.
