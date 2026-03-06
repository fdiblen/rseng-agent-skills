"""GitHub Copilot target: repo-wide instructions file.

Output layout mirrors what a consumer repository receives under .github/.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment

from ..adapters import render_to, target


@target("copilot")
def build_copilot(
    repo_root: Path, env: Environment, context: dict, target_dir: Path
) -> list[Path]:
    return [
        render_to(
            env,
            "copilot/copilot-instructions.md.j2",
            context,
            target_dir / ".github" / "copilot-instructions.md",
        )
    ]
