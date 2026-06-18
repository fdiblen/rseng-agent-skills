# Contributing

Thanks for considering a contribution.

## What to contribute where

- Content problems in source-fed material (wrong guidance, outdated
  tool, broken link in the underlying pages): usually belongs upstream
  in the content source - RSQKit
  (https://github.com/EVERSE-ResearchSoftware/RSQKit) or the
  Netherlands eScience Center guide
  (https://github.com/NLeSC/guide). This pack
  regenerates from pinned snapshots of those sources, so upstream fixes
  flow in on sync.
- Most skills are source-independent: their guidance is authored here,
  so fixes to them belong here too.
- Skill wording, triggers, structure, adapters, installer, pipeline:
  belongs here. Open an issue first for anything larger than a typo.

## Ground rules

- skills/*/references.md files and dist/ are generated - never edit them
  by hand; change the pipeline or a source's upstream pin instead.
- SKILL.md bodies are hand-authored; follow
  docs/dev/skill-authoring-template.md and keep the attribution footer.
- Small, focused commits; tests and linters green before a PR
  (`uv run pytest` in pipeline/, `npm test` in installer/).
- Content is CC-BY-4.0 (source-fed skills adapt CC-BY-4.0 sources such
  as RSQKit and the eScience Center guide), code is MIT; by contributing
  you agree your contribution is licensed the same way.

## Proposing external skills

Know a skill collection, marketplace entry or standard worth including?
Add a link to catalog.yml (status: proposed) - that is all a proposal
takes. Nothing is fetched automatically: a maintainer stages the pinned
content, reviews it and vendors accepted skill folders into skills/.
See docs/dev/catalog.md.

## Development setup

See docs/dev/architecture.md for the layout and docs/dev/pipeline.md for
running the pipeline. Python side uses uv, the installer uses npm.
