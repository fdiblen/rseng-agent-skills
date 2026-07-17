"""Cursor target: one always-on overview rule + native skills tree.

Cursor (2.4+) reads `.agents/skills/` natively with description-based
activation, which replaces the per-skill .mdc rules, the .cursor skill
copies and the .cursor commands this target used to render. What
remains under .cursor/ is a single always-apply rule carrying the
behavior baseline, plus the platform-neutral self-check.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment

from ..adapters import build_agents_skills, copy_check, render_to, target


@target("cursor")
def build_cursor(
    repo_root: Path, env: Environment, context: dict, target_dir: Path
) -> list[Path]:
    cursor_dir = target_dir / ".cursor"
    written = [
        render_to(
            env,
            "cursor/rseng-overview.mdc.j2",
            context,
            cursor_dir / "rules" / "rseng-overview.mdc",
        )
    ]
    written += build_agents_skills(repo_root, context, target_dir)
    written += copy_check(repo_root, cursor_dir)
    return written
