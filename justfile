# Development tasks. Requires uv (https://docs.astral.sh/uv/) and just.

default:
    @just --list

# Lint and check formatting
lint:
    uvx ruff check pipeline hooks adapters
    uvx ruff format --check pipeline

# Auto-fix lint findings and reformat
fix:
    uvx ruff check --fix pipeline
    uvx ruff format pipeline

# Install git pre-commit hooks
hooks:
    uvx pre-commit install
