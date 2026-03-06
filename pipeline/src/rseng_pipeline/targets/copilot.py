"""GitHub Copilot target.

Output layout mirrors what a consumer repository receives under .github/:
copilot-instructions.md (repo-wide summary), instructions/*.instructions.md
(one per skill, glob-scoped) and skills/ (canonical skill passthrough).
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment

from ..adapters import copy_skills, render_to, target


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
    for skill in context["skills"]:
        written.append(
            render_to(
                env,
                "copilot/skill.instructions.md.j2",
                {**context, "skill": skill},
                github_dir / "instructions" / f"{skill['name']}.instructions.md",
            )
        )
    copy_skills(repo_root, github_dir / "skills")
    written.extend(sorted((github_dir / "skills").rglob("SKILL.md")))
    return written
