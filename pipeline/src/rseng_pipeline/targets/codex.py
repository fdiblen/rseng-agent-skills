"""Codex CLI target: behavior-rules AGENTS.md + native skills tree.

Codex reads `.agents/skills/` natively (implicit invocation by
description match), so AGENTS.md carries only the behavior rules, the
phased-practice protocol and the self-check pointer. Command-skills
carry agents/openai.yaml with implicit invocation disabled.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment

from ..adapters import build_agents_skills, copy_check, render_to, target
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
    written = [agents_md]
    written += build_agents_skills(repo_root, context, target_dir)
    written += copy_check(repo_root, target_dir)
    return written
