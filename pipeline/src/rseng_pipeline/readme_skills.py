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


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    readme = repo_root / "README.md"
    text = readme.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit("skills-list markers missing from README.md")
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    block = skills_block(repo_root / "skills")
    readme.write_text(
        head + START + "\n\n" + block + "\n\n" + END + tail, encoding="utf-8"
    )
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
