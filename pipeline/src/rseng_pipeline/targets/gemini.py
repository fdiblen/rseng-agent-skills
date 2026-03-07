"""Gemini CLI target: extension manifest plus GEMINI.md context file."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment

from ..adapters import render_to, target


@target("gemini")
def build_gemini(
    repo_root: Path, env: Environment, context: dict, target_dir: Path
) -> list[Path]:
    return [
        render_to(
            env,
            "gemini/gemini-extension.json.j2",
            context,
            target_dir / "gemini-extension.json",
        ),
        render_to(env, "gemini/GEMINI.md.j2", context, target_dir / "GEMINI.md"),
    ]
