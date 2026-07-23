"""Gemini CLI target: extension manifest, GEMINI.md context, TOML commands.

Command bodies are reused from the Claude plugin's commands/ files with
the Claude-specific placeholders translated: ${CLAUDE_PLUGIN_ROOT} becomes
a path into the extension's bundled skills/ copy, and $ARGUMENTS becomes
Gemini's {{args}}.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment

from ..adapters import copy_check, copy_skills, render_to, target


def _gemini_body(body: str) -> str:
    translated = body.replace("${CLAUDE_PLUGIN_ROOT}/", "the extension's ")
    translated = translated.replace("$ARGUMENTS", "{{args}}")
    return translated


@target("gemini")
def build_gemini(
    repo_root: Path, env: Environment, context: dict, target_dir: Path
) -> list[Path]:
    written = [
        render_to(
            env,
            "gemini/gemini-extension.json.j2",
            context,
            target_dir / "gemini-extension.json",
        ),
        render_to(env, "gemini/GEMINI.md.j2", context, target_dir / "GEMINI.md"),
    ]
    from ..adapters import CLAUDE_ONLY_COMMANDS

    for command in context["commands"]:
        # rseng-panel orchestrates Claude subagents that do not ship in
        # the extension; keep it out of every non-Claude target.
        if command["name"] in CLAUDE_ONLY_COMMANDS:
            continue
        adapted = {**command, "body": _gemini_body(command["body"])}
        written.append(
            render_to(
                env,
                "gemini/command.toml.j2",
                {**context, "command": adapted},
                target_dir / "commands" / f"{command['name']}.toml",
            )
        )
    copy_skills(repo_root, target_dir / "skills")
    written.extend(sorted((target_dir / "skills").rglob("SKILL.md")))
    written.extend(copy_check(repo_root, target_dir))
    return written
