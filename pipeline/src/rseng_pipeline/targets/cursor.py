"""Cursor target: .cursor/rules/*.mdc.

One short always-on overview rule plus one agent-requested rule per skill
(Cursor attaches those by description relevance).
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment

from ..adapters import render_to, target


@target("cursor")
def build_cursor(
    repo_root: Path, env: Environment, context: dict, target_dir: Path
) -> list[Path]:
    rules_dir = target_dir / ".cursor" / "rules"
    written = [
        render_to(
            env,
            "cursor/rseng-overview.mdc.j2",
            context,
            rules_dir / "rseng-overview.mdc",
        )
    ]
    for skill in context["skills"]:
        written.append(
            render_to(
                env,
                "cursor/skill.mdc.j2",
                {**context, "skill": skill},
                rules_dir / f"{skill['name']}.mdc",
            )
        )
    return written
