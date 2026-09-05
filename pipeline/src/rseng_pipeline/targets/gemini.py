"""Gemini CLI target: GEMINI.md context + the native skills tree.

Gemini CLI reads workspace skills from .agents/skills/ natively (the
same unified tree Codex, Cursor and Copilot consume) with
progressive disclosure and an activate_skill confirmation, so the
target ships the canonical tree plus a GEMINI.md carrying the
behavior rules and phased protocol. The TOML command format is retired;
command-skills in the tree replace it.

A user-scoped install is a different shape. Gemini CLI loads extensions
from ~/.gemini/extensions and every one MUST carry gemini-extension.json
in its root; it reads an extension's skills from skills/ rather than
.agents/skills/, and its hooks from hooks/hooks.json. Shipping the
workspace layout to that path produced a directory that installed
cleanly and was then never loaded, so the extension is built separately.
"""

from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment

from ..adapters import build_agents_skills, copy_check, render_to, target
from ..hook_wiring import hooks_config, write_hook_scripts, write_hooks


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


@target("gemini-extension")
def build_gemini_extension(
    repo_root: Path, env: Environment, context: dict, target_dir: Path
) -> list[Path]:
    manifest = target_dir / "gemini-extension.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps(
            {
                # Gemini expects the name to match the directory it is
                # installed into, which is what the installer creates.
                "name": "rseng-agent-skills",
                "version": context["version"],
                "description": (
                    "Research software engineering practice for coding "
                    "agents: skills, workflow commands and a phased "
                    "practice-enforcement layer."
                ),
                "contextFileName": "GEMINI.md",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    written = [
        manifest,
        render_to(env, "gemini/GEMINI.md.j2", context, target_dir / "GEMINI.md"),
    ]
    written += build_agents_skills(
        repo_root, context, target_dir, tree=target_dir / "skills"
    )
    written += copy_check(repo_root, target_dir)
    # ${extensionPath} rather than a relative path: the hooks run with the
    # user's project as cwd, not the extension directory, so a relative
    # command would look for the scripts inside whatever repo is open.
    written += write_hook_scripts(repo_root, target_dir / "rseng")
    hooks_file = target_dir / "hooks" / "hooks.json"
    hooks_file.parent.mkdir(parents=True, exist_ok=True)
    hooks_file.write_text(
        json.dumps(hooks_config("gemini", root="${extensionPath}/rseng"), indent=2)
        + "\n",
        encoding="utf-8",
    )
    written.append(hooks_file)
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
