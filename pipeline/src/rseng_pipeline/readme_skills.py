"""Regenerate the skills list in the root README.md.

Rewrites the block between the skills-list markers from the skills'
own frontmatter descriptions, so the README never drifts from the
actual pack contents.

Usage: python -m rseng_pipeline.readme_skills
"""

from __future__ import annotations

from pathlib import Path

import frontmatter

from .adapters import _brief

START = "<!-- skills-list:start (generated - do not edit by hand) -->"
END = "<!-- skills-list:end -->"
CMD_START = "<!-- commands-list:start (generated - do not edit by hand) -->"
CMD_END = "<!-- commands-list:end -->"
AGENT_START = "<!-- agents-list:start (generated - do not edit by hand) -->"
AGENT_END = "<!-- agents-list:end -->"


def _spell(n: int) -> str:
    words = {
        6: "six",
        7: "seven",
        8: "eight",
        9: "nine",
        10: "ten",
        11: "eleven",
        12: "twelve",
        13: "thirteen",
        14: "fourteen",
        15: "fifteen",
    }
    return words.get(n, str(n))


def skills_block(skills_dir: Path) -> str:
    lines = []
    for skill_dir in sorted(skills_dir.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        post = frontmatter.loads(skill_md.read_text(encoding="utf-8"))
        name = post.get("name", skill_dir.name)
        brief = _brief(str(post.get("description", "")))
        if brief.startswith("Covers "):
            brief = brief[len("Covers ") :]
        elif brief.startswith("Explains "):
            brief = brief[len("Explains ") :]
        lines.append(f"| `{name}` | {brief} |")
    return "\n".join(["| Skill | Purpose |", "| --- | --- |", *lines])


def commands_block(commands_dir: Path) -> str:
    lines = ["| Command | Purpose |", "| --- | --- |"]
    for path in sorted(commands_dir.glob("*.md")):
        post = frontmatter.loads(path.read_text(encoding="utf-8"))
        lines.append(f"| `/{path.stem}` | {post.get('description', '')} |")
    return "\n".join(lines)


def agents_block(agents_dir: Path) -> str:
    lines = ["| Agent | Purpose |", "| --- | --- |"]
    for path in sorted(agents_dir.glob("*.md")):
        post = frontmatter.loads(path.read_text(encoding="utf-8"))
        desc = " ".join(str(post.get("description", "")).split())
        first = desc.split(". ")[0].rstrip(".") + "."
        lines.append(f"| `{post.get('name', path.stem)}` | {first} |")
    return "\n".join(lines)


def _replace_block(text: str, start: str, end: str, block: str) -> str:
    if start not in text or end not in text:
        raise SystemExit(f"markers missing from README.md: {start}")
    head, rest = text.split(start, 1)
    _, tail = rest.split(end, 1)
    return head + start + "\n\n" + block + "\n\n" + end + tail


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    readme = repo_root / "README.md"
    text = readme.read_text(encoding="utf-8")
    block = skills_block(repo_root / "skills")
    text = _replace_block(text, START, END, block)
    text = _replace_block(
        text, CMD_START, CMD_END, commands_block(repo_root / "commands")
    )
    text = _replace_block(
        text, AGENT_START, AGENT_END, agents_block(repo_root / "agents")
    )
    readme.write_text(text, encoding="utf-8")
    count = block.count("\n") - 1  # minus the two table header rows

    import re

    commands = len(list((repo_root / "commands").glob("*.md")))
    agents = len(list((repo_root / "agents").glob("*.md")))
    for manifest in (
        repo_root / ".claude-plugin" / "marketplace.json",
        repo_root / ".claude-plugin" / "plugin.json",
    ):
        raw = manifest.read_text(encoding="utf-8")
        updated = re.sub(r"\d+ skills", f"{count} skills", raw)
        updated = re.sub(
            r"\w+ workflow commands", f"{_spell(commands)} workflow commands", updated
        )
        updated = re.sub(r"\w+ subagents", f"{_spell(agents)} subagents", updated)
        if updated != raw:
            manifest.write_text(updated, encoding="utf-8")
    for doc in (
        repo_root / "docs" / "user" / "quickstart.md",
        repo_root / "docs" / "user" / "installing.md",
    ):
        if doc.is_file():
            raw = doc.read_text(encoding="utf-8")
            updated = re.sub(r"\d+ skills", f"{count} skills", raw)
            if updated != raw:
                doc.write_text(updated, encoding="utf-8")
    print(f"README skills list regenerated ({count} skills; counts synced)")


if __name__ == "__main__":
    main()
