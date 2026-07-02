"""Cursor target: .cursor/rules/*.mdc, commands, skills and self-check.

One short always-on overview rule plus one agent-requested rule per skill
(Cursor attaches those by description relevance). Rules carry the skill's
related-skills list and point at the full canonical skill text copied
into .cursor/skills/. The plugin's commands become Cursor custom
commands (.cursor/commands/*.md) and the platform-neutral self-check
lands in .cursor/rseng-check/.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment

from ..adapters import copy_check, copy_skills, render_to, target


def _cursor_body(body: str) -> str:
    translated = body.replace("${CLAUDE_PLUGIN_ROOT}/", ".cursor/")
    return translated.replace("$ARGUMENTS", "the arguments given with the command")


@target("cursor")
def build_cursor(
    repo_root: Path, env: Environment, context: dict, target_dir: Path
) -> list[Path]:
    cursor_dir = target_dir / ".cursor"
    rules_dir = cursor_dir / "rules"
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
    for command in context["commands"]:
        adapted = {**command, "body": _cursor_body(command["body"])}
        written.append(
            render_to(
                env,
                "cursor/command.md.j2",
                {**context, "command": adapted},
                cursor_dir / "commands" / f"{command['name']}.md",
            )
        )
    copy_skills(repo_root, cursor_dir / "skills")
    written.extend(sorted((cursor_dir / "skills").rglob("SKILL.md")))
    written.extend(copy_check(repo_root, cursor_dir))
    return written
