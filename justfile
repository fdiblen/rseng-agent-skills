# Development tasks. Requires uv (https://docs.astral.sh/uv/) and just.

default:
    @just --list

# Lint and check formatting, at the same scope and version as CI
lint:
    uvx ruff@0.16.5 check pipeline hooks adapters
    uvx ruff@0.16.5 format --check pipeline hooks adapters

# Auto-fix lint findings and reformat
fix:
    uvx ruff@0.16.5 check --fix pipeline hooks adapters
    uvx ruff@0.16.5 format pipeline hooks adapters

# Install git pre-commit hooks
hooks:
    uvx pre-commit install

# Everything CI runs, in CI's order. Run this before opening a PR.
check: lint
    uv run --directory pipeline --group dev pytest ../hooks/tests -q
    uv run --directory pipeline python -m rseng_pipeline.skill_lint
    uv run --directory pipeline python -m rseng_pipeline.references
    uv run --directory pipeline python -m rseng_pipeline.related_skills
    uv run --directory pipeline python -m rseng_pipeline.skill_directory
    uv run --directory pipeline python -m rseng_pipeline.token_budget
    uv run --directory pipeline python -m rseng_pipeline.build_adapters
    # after build_adapters: these run the self-check as dist/ ships it
    uv run --directory pipeline --group dev pytest ../adapters/tests -q
    uv run --directory pipeline python -m rseng_pipeline.readme_skills
    git diff --exit-code README.md AGENTS.md hooks .claude-plugin docs skills codemeta.json .zenodo.json
    uv run --directory pipeline python -m rseng_pipeline.catalog check
    uvx --with charset-normalizer --from reuse reuse lint
    cd installer && npm ci && npm run build && npm test
