# Contributing

Thanks for considering a contribution.

## What to contribute where

- Content problems (wrong guidance, outdated tool, broken link in the
  underlying material): usually belongs upstream in RSQKit -
  https://github.com/EVERSE-ResearchSoftware/RSQKit. This pack
  regenerates from RSQKit, so upstream fixes flow in on sync.
- Skill wording, triggers, structure, adapters, installer, pipeline:
  belongs here. Open an issue first for anything larger than a typo.

## Ground rules

- skills/*/references/ folders and dist/ are generated - never edit them
  by hand; change the pipeline or the upstream pin instead.
- SKILL.md bodies are hand-authored; follow
  docs/dev/skill-authoring-template.md and keep the attribution footer.
- Small, focused commits; tests and linters green before a PR
  (`uv run pytest` in pipeline/, `npm test` in installer/).
- Content is CC-BY-4.0 (adapted from RSQKit), code is MIT; by
  contributing you agree your contribution is licensed the same way.

## Development setup

See docs/dev/architecture.md for the layout and docs/dev/pipeline.md for
running the pipeline. Python side uses uv, the installer uses npm.
