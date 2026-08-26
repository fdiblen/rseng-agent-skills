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
- Small, focused commits; linters green before a PR, and `npm test` in
  installer/ if you touched the CLI. The pipeline is verified by
  regenerating its output and diffing, which CI does.
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

Python side uses uv, the installer uses npm. A fresh clone has neither the
generated adapter bundles nor a built CLI, so do both once before anything
that installs the pack:

```bash
uv run --directory pipeline python -m rseng_pipeline.build_adapters
cd installer && npm ci && npm run build
```

`dist/` and `installer/dist/` are build output and are not committed. See
docs/dev/architecture.md for the layout and docs/dev/pipeline.md for running
the pipeline.
