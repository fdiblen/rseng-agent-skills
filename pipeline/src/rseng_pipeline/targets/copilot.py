"""GitHub Copilot target: repo instructions + native skills tree.

Copilot reads `.agents/skills/` natively, and skills work across the
whole Copilot surface (agent mode, CLI, code review, cloud agents) -
unlike the per-skill instruction files and prompt files this target
used to render, which never reached cloud agents and attached ~124KB
of always-on instructions per request. What remains under .github/ is
the repo-wide behavior instructions and the self-check.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment

from ..adapters import build_agents_skills, copy_check, render_to, target


@target("copilot")
def build_copilot(
    repo_root: Path, env: Environment, context: dict, target_dir: Path
) -> list[Path]:
    github_dir = target_dir / ".github"
    written = [
        render_to(
            env,
            "copilot/copilot-instructions.md.j2",
            context,
            github_dir / "copilot-instructions.md",
        )
    ]
    written += build_agents_skills(repo_root, context, target_dir)
    written += copy_check(repo_root, github_dir)
    return written
