# rseng-agent-skills

Research software engineering (RSEng) skills for AI coding agents:
67 skills covering the practices that make research software good -
testing, CI/CD, documentation, licensing, citation, FAIR, publishing,
reproducibility, code review, code quality, maintenance, planning and
workflows - built into native formats for the major agents.

Skills teach while doing: each carries curated, verified "Learn more"
links so the guidance stays traceable to real material rather than
generic.

Part of the skill content was originally adapted from
community-maintained CC-BY-4.0 material. This project is independent
of, and not endorsed by, those projects; full credits are in
ATTRIBUTION.md.

## Quick start (TL;DR)

```bash
# Claude Code: install as a plugin
/plugin marketplace add fdiblen/rseng-agent-skills
/plugin install rseng-agent-skills

# any other supported agent (auto-detected):
npx rseng-agent-skills install          # or: install copilot|cursor|codex|gemini
npx rseng-agent-skills doctor           # verify the install
```

Then, in your agent: run `/rseng-kickoff` in a new project, `/rseng-check`
in an existing one - or just start working; skills activate on their
own, keep an AI usage declaration (aidecl.yaml), and suggest research
software best practice as you go.

## Agent support

| Agent | What you get | Install |
|---|---|---|
| Claude Code | all skills, workflow commands and subagents | `/plugin marketplace add fdiblen/rseng-agent-skills` then `/plugin install rseng-agent-skills` |
| GitHub Copilot | repo instructions + per-skill instructions + skills | `npx rseng-agent-skills install copilot` |
| Cursor | always-on overview + per-topic rules | `npx rseng-agent-skills install cursor` |
| Codex CLI | AGENTS.md + skills folders | `npx rseng-agent-skills install codex` |
| Gemini CLI | extension with context, commands and skills | `npx rseng-agent-skills install gemini` |
| others (Zed, opencode, Goose, ...) | AGENTS.md + standard SKILL.md folders work as-is | `npx rseng-agent-skills install claude` (standard layout) |

The `npx rseng-agent-skills` CLI detects which agents you use and installs the
right files; `--dry-run` previews, `update` refreshes managed files
without touching your edits, and `doctor` checks install health.

## What is inside

- skills/ - canonical SKILL.md folders (agentskills.io format), one per
  topic, each with a generated references.md (verified learn-more
  links)
- commands/, agents/, hooks/ - Claude Code slash commands, subagents
  and session hooks that keep the skills actively used
- pipeline/ - the build pipeline that derives everything generated
  (references, directory, relations, adapter outputs) from the skills
- installer/ - the TypeScript CLI published to npm as `rseng-agent-skills`

## Skills

<!-- skills-list:start (generated - do not edit by hand) -->

| Skill | Purpose |
| --- | --- |
| `rseng-agent-security` | operating AI coding agents securely |
| `rseng-ai-declaration` | declaring AI involvement with the AI Declaration Format (https://ai-declaration.org) |
| `rseng-archiving` | long-term archiving of research software and data |
| `rseng-big-data-processing` | processing research data that outgrows one machine's memory |
| `rseng-ci-cd` | continuous integration and delivery for research software |
| `rseng-citation-hygiene` | verifying that every citation is real, correct and current |
| `rseng-citation-metadata` | making research software citable and contributors credited |
| `rseng-code-quality` | writing readable research code and structuring software projects |
| `rseng-code-review` | reviewing existing code and whole projects, not just new diffs |
| `rseng-community-governance` | building and governing a community around research software |
| `rseng-community-metrics` | measuring community health with CHAOSS-style metrics |
| `rseng-contributor-onboarding` | turning users into contributors and contributors into regulars |
| `rseng-data-management` | research data management around software |
| `rseng-data-management-plans` | data management plans (DMPs) for research projects |
| `rseng-debugging` | systematic debugging of research software |
| `rseng-defensive-coding` | defenses against silently wrong research results |
| `rseng-dependency-management` | the full lifecycle of third-party dependencies |
| `rseng-discovery` | discovering the research landscape around a topic or project |
| `rseng-documentation` | how to document research software at every level |
| `rseng-fact-checking` | verifying facts and sources at the content level |
| `rseng-fair-ml` | applying FAIR principles to machine learning artifacts |
| `rseng-fair-software` | how to apply the FAIR principles - findable, accessible, interoperable, reusable - to research software, and how... |
| `rseng-fairguard` | assessing research software against the 17 FAIR4RS principles with FAIRGuard (https://www.fairguard.org) |
| `rseng-gpu-computing` | GPU and accelerator programming for research software |
| `rseng-green-computing` | the environmental footprint of research computing |
| `rseng-honesty` | responding when concealment or misrepresentation is requested |
| `rseng-hpc-computing` | working effectively on high-performance computing clusters |
| `rseng-human-verification` | the human's side of AI-assisted research software |
| `rseng-language-guides` | language-specific research software practice |
| `rseng-legacy-code` | working safely with inherited research code |
| `rseng-lessons-learned` | capturing and reusing what a project learns |
| `rseng-license-compliance` | license compliance engineering |
| `rseng-licensing` | how to license research software |
| `rseng-maintenance-sustainability` | keeping research software alive and responsible over time |
| `rseng-management-planning` | planning research software work |
| `rseng-notebooks` | engineering discipline for computational notebooks |
| `rseng-numerical-accuracy` | floating-point correctness in research code |
| `rseng-open-science-practices` | the researcher-facing open science workflow |
| `rseng-open-source-migration` | migrating research code from commercial, license-bound platforms to open source alternatives |
| `rseng-pair-programming` | the agent as an effective pair programmer and pull-request review buddy for research software |
| `rseng-performance-profiling` | making research code faster with evidence |
| `rseng-project-kickoff` | starting a new research software project with a short kickoff interview |
| `rseng-project-scaffolding` | starting research software projects from maintained templates and keeping them in sync |
| `rseng-project-tracking` | the operational side of running a research software project |
| `rseng-provenance` | capturing and packaging the provenance of software and data |
| `rseng-publishing-releasing` | the release lifecycle of research software |
| `rseng-quality-framework` | The entry point and router for this pack |
| `rseng-regulatory-compliance` | checking research code and data against data-protection and AI regulation |
| `rseng-reproducibility` | end-to-end computational reproducibility |
| `rseng-reproducible-environments` | making research software environments reproducible |
| `rseng-research-integrity` | integrity checks on research outputs before submission or release |
| `rseng-science-communication` | communicating research software outward to research audiences |
| `rseng-scientific-file-formats` | choosing and handling scientific data formats in code |
| `rseng-scientific-visualization` | visualization of scientific data beyond publication figures |
| `rseng-security` | securing research software and its supply chain |
| `rseng-software-design` | designing research software |
| `rseng-software-metrics` | measuring code health quantitatively |
| `rseng-software-peer-review` | community peer review of research software |
| `rseng-software-publishing` | publishing research software through its distribution channels |
| `rseng-software-reuse` | discovering and reusing existing research software instead of rebuilding it, using Research Software Directory... |
| `rseng-storytelling` | telling the story of research data, software and projects to broad audiences |
| `rseng-testing` | how to test research software |
| `rseng-trainer` | teaching research software skills while working |
| `rseng-user-support` | running user support as an operation for research software |
| `rseng-ux-accessibility` | user experience and accessibility for research software |
| `rseng-version-control-review` | using version control effectively for research software and the PR-time review process |
| `rseng-workflows` | building, choosing, discovering, describing, and sharing computational workflows with workflow management... |

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

## Versioning

Semantic versioning against the pack content: patch = regenerated
content only, minor = skill body updates or new skills, major = skills
removed or renamed in a way that reshapes the skill set.

## Attribution

Part of the skill content was originally adapted from
community-maintained material published under CC-BY-4.0. Full credits
live in [ATTRIBUTION.md](ATTRIBUTION.md), the canonical record of that
content provenance. The adaptations are independent and not endorsed
by the original projects.
