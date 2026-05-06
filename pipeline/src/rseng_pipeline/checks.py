"""Post-render checks for adapter outputs.

Run by the build command after each target renders; a non-empty problem
list fails the build. Checks are format-driven: character budgets for
context files agents load whole, frontmatter validation for rule and
instruction files, TOML validity for Gemini commands, and residue checks
for placeholders that must never reach a non-Claude target.
"""

from __future__ import annotations

import json
from pathlib import Path

import frontmatter
import tomllib

# Context files that agents load in full get explicit budgets.
SIZE_BUDGETS = {
    "copilot-instructions.md": 16 * 1024,
    "GEMINI.md": 24 * 1024,
    "AGENTS.md": 32 * 1024,
}

_FRONTMATTER_REQUIRED = {
    ".instructions.md": ("description", "applyTo"),
    ".mdc": ("description", "alwaysApply"),
}


def _check_file(path: Path, commit_stamp: str | None = None) -> list[str]:
    problems = []
    rel = path.name
    text = path.read_text(encoding="utf-8")

    if commit_stamp and commit_stamp not in text:
        problems.append(f"{rel}: missing provenance stamp {commit_stamp!r}")

    budget = SIZE_BUDGETS.get(path.name)
    if budget and len(text.encode()) > budget:
        problems.append(f"{rel}: {len(text.encode())} bytes over {budget} budget")

    for suffix, required in _FRONTMATTER_REQUIRED.items():
        if path.name.endswith(suffix):
            meta = frontmatter.loads(text).metadata
            for field in required:
                if field not in meta:
                    problems.append(f"{rel}: missing frontmatter field {field!r}")

    if path.suffix == ".toml":
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as error:
            problems.append(f"{rel}: invalid TOML: {error}")
        else:
            if not data.get("description") or not data.get("prompt"):
                problems.append(f"{rel}: TOML command needs description and prompt")

    if path.suffix == ".json":
        try:
            json.loads(text)
        except json.JSONDecodeError as error:
            problems.append(f"{rel}: invalid JSON: {error}")

    if "CLAUDE_PLUGIN_ROOT" in text:
        problems.append(f"{rel}: CLAUDE_PLUGIN_ROOT placeholder leaked")
    if "{%" in text and path.suffix in {".md", ".mdc"} and "SKILL" not in path.name:
        problems.append(f"{rel}: unrendered template or liquid residue")

    return problems


def check_target(target_dir: Path, commit: str | None = None) -> list[str]:
    """Check every rendered file under one target's dist directory.

    When ``commit`` is given, every rendered (non-passthrough) file must
    carry its 8-character provenance stamp.
    """
    stamp = commit[:8] if commit else None
    problems = []
    for path in sorted(target_dir.rglob("*")):
        if not path.is_file():
            continue
        if (
            "references" in path.parts
            or "data" in path.parts
            or path.name == "SKILL.md"
            or path.name == "references.md"
        ):
            continue  # canonical passthrough content is validated at its source
        for problem in _check_file(path, commit_stamp=stamp):
            problems.append(f"{target_dir.name}/{problem}")
    return problems
