# Contributing

Thanks for considering a contribution.

## What to contribute where

- Everything belongs in this repository: skill content and wording,
  triggers, structure, adapters, installer, pipeline. Open an issue
  first for anything larger than a typo.

## Ground rules

- skills/*/references.md files, the marker-delimited blocks in
  SKILL.md/AGENTS.md/README.md, hooks/*.json and dist/ are generated -
  never edit them by hand; change the skill's own content or the
  pipeline and regenerate.
- SKILL.md bodies are hand-authored; follow the authoring template in
  the developer docs.
- Small, focused commits; tests and linters green before a PR
  (`uv run pytest` in pipeline/, `npm test` in installer/).
- Content is CC-BY-4.0 (part of it was originally adapted from CC-BY
  sources credited in ATTRIBUTION.md), code is MIT; by contributing
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
