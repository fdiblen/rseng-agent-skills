"""Codex CLI target: generated AGENTS.md plus canonical skills passthrough.

Codex reads at most 32 KiB of project docs per file by default, so the
generated AGENTS.md is size-checked at build time.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment

from ..adapters import copy_skills, render_to, target
from ..checks import SIZE_BUDGETS

AGENTS_MD_BUDGET = SIZE_BUDGETS["AGENTS.md"]


@target("codex")
def build_codex(
    repo_root: Path, env: Environment, context: dict, target_dir: Path
) -> list[Path]:
    agents_md = render_to(env, "codex/AGENTS.md.j2", context, target_dir / "AGENTS.md")
    size = agents_md.stat().st_size
    if size > AGENTS_MD_BUDGET:
        raise RuntimeError(
            f"AGENTS.md is {size} bytes, over the {AGENTS_MD_BUDGET} budget"
        )
    copy_skills(repo_root, target_dir / "skills")
    return [agents_md, *sorted((target_dir / "skills").rglob("SKILL.md"))]
