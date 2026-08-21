"""Gemini CLI target: GEMINI.md context + the native skills tree.

Gemini CLI reads workspace skills from .agents/skills/ natively (the
same unified tree Codex, Cursor and Copilot consume) with
progressive disclosure and an activate_skill confirmation, so the
target ships the canonical tree plus a GEMINI.md carrying the
behavior rules and phased protocol. The former extension format
(gemini-extension.json, TOML commands, bundled skills/ copies) is
retired; command-skills in the tree replace the TOML commands.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment

from ..adapters import build_agents_skills, copy_check, render_to, target
from ..hook_wiring import write_hooks


@target("gemini")
def build_gemini(
    repo_root: Path, env: Environment, context: dict, target_dir: Path
) -> list[Path]:
    written = [
        render_to(env, "gemini/GEMINI.md.j2", context, target_dir / "GEMINI.md"),
    ]
    written += build_agents_skills(repo_root, context, target_dir)
    written += copy_check(repo_root, target_dir)
    # The proactive layer, for the agents whose CLI runs hooks.
    written += write_hooks(repo_root, "gemini", target_dir)
    return written


@target("antigravity")
def build_antigravity(
    repo_root: Path, env: Environment, context: dict, target_dir: Path
) -> list[Path]:
    written = [
        render_to(env, "gemini/GEMINI.md.j2", context, target_dir / "GEMINI.md"),
        render_to(env, "codex/AGENTS.md.j2", context, target_dir / "AGENTS.md"),
    ]
    written += build_agents_skills(repo_root, context, target_dir)
    written += copy_check(repo_root, target_dir)
    return written
