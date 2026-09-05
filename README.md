# rseng-agent-skills

Research software engineering practice, packaged so a coding agent
actually follows it. 67 skills covering how to test, document, license,
cite, package, release and review research software, built into the
native format each major agent already reads.

The point is not a checklist the agent recites. Skills activate on their
own while it works, and each one carries curated links that were checked
by a link checker, so its advice stays traceable to real material rather
than to whatever the model half-remembers.

## Install

Claude Code, as a plugin - this route also brings the commands, the
subagents and the session hooks:

```
/plugin marketplace add fdiblen/rseng-agent-skills
/plugin install rseng-agent-skills
```

Any other agent, through the CLI:

```bash
npx rseng-agent-skills install     # detects the agents you use
npx rseng-agent-skills doctor      # check what landed and whether it is current
```

`install` takes an agent name to be explicit (`install codex`),
`--dry-run` previews without writing, and `update` refreshes managed
files while leaving your own edits alone.

Bare `install` detects every agent it finds and installs for all of
them, which for some targets means writing under `~/.claude`, `~/.gemini`
or `~/.codex` rather than into the repository. It lists those paths and
asks before writing outside the current project; `--yes` skips the
question. See [docs/user/installing.md](docs/user/installing.md) for what
each agent gets and where.

Everything written is recorded in a per-agent manifest, so nothing is
one-way:

```bash
npx rseng-agent-skills uninstall            # remove it again
npx rseng-agent-skills uninstall --dry-run  # or just see what that would take
```

`uninstall` removes the files it installed and leaves anything you have
edited since, naming what it kept.

Then just start working. Or run `/rseng-kickoff` in a new project and
`/rseng-check` in an existing one.

Nothing here pre-approves any tool or permission. Where hooks are
installed your agent shows its normal one-time trust prompt for the hook
file, exactly as it would for any project config - that is the agent
asking, not the pack. On a first run the agent may also pause before its
first write while it opens the relevant skills; that is the pack working
and it resolves itself. If you want it off, create an empty
`.rseng-agent-skills-relaxed` file yourself - the agent is not permitted
to create it, so it cannot switch off its own checks.

## Agent support

| Agent | What you get | Install |
|---|---|---|
| Claude Code | skills, commands, subagents and session hooks | `/plugin install rseng-agent-skills` after adding the marketplace |
| Codex CLI | AGENTS.md, `.agents/skills`, the self-check, and hook config | `npx rseng-agent-skills install codex` |
| Gemini CLI | extension with context, commands and skills, and hook config | `npx rseng-agent-skills install gemini` |
| Google Antigravity | GEMINI.md, AGENTS.md and `.agents/skills` | `npx rseng-agent-skills install antigravity` |
| GitHub Copilot | repository instructions and `.agents/skills` | `npx rseng-agent-skills install copilot` |
| Cursor | always-on overview rule and `.agents/skills` | `npx rseng-agent-skills install cursor` |
| Zed, opencode, Goose and others | AGENTS.md and standard SKILL.md folders, which they read as-is | `npx rseng-agent-skills install codex` |

Only the Claude plugin and the codex and gemini installs carry hooks;
`install claude` copies skills, commands and subagents and adds none.

## How it works

Three things keep the guidance in play rather than on a shelf:

- The skills are written to trigger themselves. Each declares what it
  covers and when it should fire, so the agent opens the licensing skill
  when it is about to write a LICENSE, not because you asked it to.
- A router skill holds the full directory, grouped into the same
  clusters used below, so nothing is reachable only by luck.
- Where the agent supports hooks, they run at session start, after
  writes and at stop. They are not advisory: the write gate holds the
  first write until the start-of-work steps are recorded, and the stop
  check holds the session until the practice artifacts are there or a
  reason is recorded. Both explain themselves, and an empty
  `.rseng-agent-skills-relaxed` file turns the whole layer off.

Everything generated - each skill's references, the directory, the
related-skills graph and the per-agent bundles - is derived from the
skills themselves by the pipeline, and CI fails if a committed file
disagrees with what the pipeline produces.

## Declaring AI involvement

Disclosure is one of the practices the pack applies to your work, not
just something it advises. When an agent with these skills installed
writes code for you it creates `aidecl.yaml` at your project root, keeps
it current as the work changes, and commits it with that work - it is
project content in the
[AI Declaration Format](https://ai-declaration.org), recording which
tools and models touched the project, when, on what, and in what
proportion. It also adds a short README footnote so a reader can find it.

`/rseng-declare` creates or updates the declaration on demand, and the
`rseng-ai-declaration` skill covers what belongs in one, which optional
sections to open as AI use deepens, and how much detail is honest.

## Skills

<!-- skills-list:start (generated - do not edit by hand) -->

### Start here

| Skill | Purpose |
| --- | --- |
| `rseng-quality-framework` | The entry point and router for this pack |

### Core engineering

| Skill | Purpose |
| --- | --- |
| `rseng-testing` | how to test research software |
| `rseng-ci-cd` | continuous integration and delivery for research software |
| `rseng-code-quality` | writing readable research code and structuring software projects |
| `rseng-software-design` | designing research software |
| `rseng-defensive-coding` | defenses against silently wrong research results |
| `rseng-debugging` | systematic debugging of research software |
| `rseng-version-control-review` | using version control effectively for research software and the PR-time review process |
| `rseng-software-metrics` | measuring code health quantitatively |
| `rseng-pair-programming` | the agent as an effective pair programmer and pull-request review buddy for research software |
| `rseng-code-review` | reviewing existing code and whole projects, not just new diffs |
| `rseng-project-scaffolding` | starting research software projects from maintained templates and keeping them in sync |

### Reproducibility and workflows

| Skill | Purpose |
| --- | --- |
| `rseng-reproducible-environments` | making research software environments reproducible |
| `rseng-reproducibility` | end-to-end computational reproducibility |
| `rseng-workflows` | building, choosing, discovering, describing, and sharing computational workflows with workflow management... |
| `rseng-provenance` | capturing and packaging the provenance of software and data |
| `rseng-notebooks` | engineering discipline for computational notebooks |

### Research data

| Skill | Purpose |
| --- | --- |
| `rseng-data-management` | research data management around software |
| `rseng-scientific-file-formats` | choosing and handling scientific data formats in code |
| `rseng-big-data-processing` | processing research data that outgrows one machine's memory |
| `rseng-data-management-plans` | data management plans (DMPs) for research projects |

### Numerics and performance

| Skill | Purpose |
| --- | --- |
| `rseng-numerical-accuracy` | floating-point correctness in research code |
| `rseng-performance-profiling` | making research code faster with evidence |
| `rseng-gpu-computing` | GPU and accelerator programming for research software |
| `rseng-hpc-computing` | working effectively on high-performance computing clusters |

### Publishing, credit and reuse

| Skill | Purpose |
| --- | --- |
| `rseng-publishing-releasing` | the release lifecycle of research software |
| `rseng-software-publishing` | publishing research software through its distribution channels |
| `rseng-archiving` | long-term archiving of research software and data |
| `rseng-citation-metadata` | making research software citable and contributors credited |
| `rseng-citation-hygiene` | verifying that every citation is real, correct and current |
| `rseng-licensing` | how to license research software |
| `rseng-license-compliance` | license compliance engineering |
| `rseng-fair-software` | how to apply the FAIR principles - findable, accessible, interoperable, reusable - to research software... |
| `rseng-fair-ml` | applying FAIR principles to machine learning artifacts |
| `rseng-fairguard` | assessing research software against the 17 FAIR4RS principles with FAIRGuard (https://www.fairguard.org) |
| `rseng-software-reuse` | discovering and reusing existing research software instead of rebuilding it... |
| `rseng-discovery` | discovering the research landscape around a topic or project |
| `rseng-dependency-management` | the full lifecycle of third-party dependencies |
| `rseng-software-peer-review` | community peer review of research software |
| `rseng-open-science-practices` | the researcher-facing open science workflow |

### Integrity, security and compliance

| Skill | Purpose |
| --- | --- |
| `rseng-security` | securing research software and its supply chain |
| `rseng-agent-security` | operating AI coding agents securely |
| `rseng-regulatory-compliance` | checking research code and data against data-protection and AI regulation |
| `rseng-research-integrity` | integrity checks on research outputs before submission or release |
| `rseng-fact-checking` | verifying facts and sources at the content level |
| `rseng-honesty` | responding when concealment or misrepresentation is requested |
| `rseng-human-verification` | the human's side of AI-assisted research software |
| `rseng-ai-declaration` | declaring AI involvement with the AI Declaration Format (https://ai-declaration.org) |

### Community and people

| Skill | Purpose |
| --- | --- |
| `rseng-community-governance` | building and governing a community around research software |
| `rseng-community-metrics` | measuring community health with CHAOSS-style metrics |
| `rseng-contributor-onboarding` | turning users into contributors and contributors into regulars |
| `rseng-user-support` | running user support as an operation for research software |
| `rseng-trainer` | teaching research software skills while working |

### Communication and interfaces

| Skill | Purpose |
| --- | --- |
| `rseng-documentation` | how to document research software at every level |
| `rseng-science-communication` | communicating research software outward to research audiences |
| `rseng-storytelling` | telling the story of research data, software and projects to broad audiences |
| `rseng-ux-accessibility` | user experience and accessibility for research software |

### Planning and operations

| Skill | Purpose |
| --- | --- |
| `rseng-management-planning` | planning research software work |
| `rseng-project-kickoff` | starting a new research software project with a short kickoff interview |
| `rseng-project-tracking` | the operational side of running a research software project |
| `rseng-lessons-learned` | capturing and reusing what a project learns |
| `rseng-maintenance-sustainability` | keeping research software alive and responsible over time |
| `rseng-green-computing` | the environmental footprint of research computing |

### Specialized

| Skill | Purpose |
| --- | --- |
| `rseng-language-guides` | language-specific research software practice |
| `rseng-legacy-code` | working safely with inherited research code |
| `rseng-open-source-migration` | migrating research code from commercial, license-bound platforms to open source alternatives |
| `rseng-scientific-visualization` | visualization of scientific data beyond publication figures |

<!-- skills-list:end -->

## Commands

<!-- commands-list:start (generated - do not edit by hand) -->

| Command | Purpose |
| --- | --- |
| `/rseng-check` | Assess this repository against research software engineering practice |
| `/rseng-cite` | Generate CITATION.cff and codemeta.json for this repository |
| `/rseng-declare` | Create or update the aidecl.yaml AI usage declaration |
| `/rseng-deps` | Audit this project's dependencies on all six axes |
| `/rseng-digest` | Draft the high-level project log digest for the period |
| `/rseng-integrity` | Pre-submission integrity battery for manuscript and results |
| `/rseng-kickoff` | Interview the user and set up a new research software project |
| `/rseng-lesson` | Record a lesson learned and draft its prevention artifact |
| `/rseng-metrics` | Code and community health metrics snapshot |
| `/rseng-onboard` | Generate the onboarding checklist for this project |
| `/rseng-panel` | Run a panel of expert agents with specific roles and synthesize |
| `/rseng-plan` | Draft a Software Management Plan (SMP) skeleton for this project |
| `/rseng-release` | Run the pre-release checklist and prepare the release |
| `/rseng-reproduce` | Clean-room reproduction check of this repository |

<!-- commands-list:end -->

## Agents

<!-- agents-list:start (generated - do not edit by hand) -->

| Agent | Purpose |
| --- | --- |
| `rseng-auditor` | Read-only research software quality auditor. |
| `rseng-compliance-officer` | Read-only regulatory and license compliance sweep. |
| `rseng-librarian` | Read-only citation and claim verifier. |
| `rseng-mentor` | Teaching-focused mentor for research software skills. |
| `rseng-reviewer` | Research software codebase reviewer that fixes what it finds. |
| `rseng-scout` | Read-only reuse and dependency scout. |

<!-- agents-list:end -->

## Repository layout

- `skills/` - one folder per skill in the agentskills.io SKILL.md
  format, each with a generated `references.md`
- `commands/`, `agents/`, `hooks/` - Claude Code slash commands,
  subagents and session hooks
- `pipeline/` - the build that derives everything generated above from
  the skills
- `installer/` - the TypeScript CLI published to npm as
  `rseng-agent-skills`
- `adapters/` - templates the pipeline renders into each agent's format

## Versioning

Semantic versioning against the pack content: patch = regenerated
content only, minor = skill body updates or new skills, major = skills
removed or renamed in a way that reshapes the skill set.

## License

Two licences, because there are two kinds of thing here. The code -
the pipeline, the installer, the hooks, the self-check - is
[MIT](LICENSE). The skill content under `skills/` and the documentation
are [CC-BY-4.0](LICENSE-content), which asks that you keep the credit
with the text if you redistribute it. Installing the pack places both
licence texts and `ATTRIBUTION.md` alongside the content it copies, so
the terms travel with the material.

The bundled Research Software Directory snapshots under
`skills/rseng-software-reuse/data/` carry no upstream licence and are
redistributed as factual catalogue data; see
[LICENSES/LicenseRef-RSD-metadata-undeclared.txt](LICENSES/LicenseRef-RSD-metadata-undeclared.txt).

## Attribution

Part of the skill content was originally adapted from
community-maintained material published under CC-BY-4.0. Full credits
live in [ATTRIBUTION.md](ATTRIBUTION.md), the canonical record of that
content provenance. The adaptations are independent and not endorsed
by the original projects.
