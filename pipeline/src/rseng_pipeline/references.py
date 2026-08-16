"""Generate each skill's references.md from its own SKILL.md.

Every skill maintains its verified "Learn more" links inside SKILL.md;
this module derives the references.md file beside it so agents have one
predictable place to find vetted pointers. No external content sources
are involved: the skill file is the single source of truth.
"""

from __future__ import annotations

import re
from pathlib import Path

GENERATED_HEADER = (
    "<!-- Generated file - do not edit. Derived by the rseng-agent-skills\n"
    "     pipeline from this skill's own curated links in SKILL.md. -->\n\n"
)

_MARKER = re.compile(r"Learn more \(verified[^)]*\)\s*:?")


def extract_curated(skill_md: str) -> list[str]:
    """Pull the Learn-more bullets out of a skill's SKILL.md.

    Accepts both marker spellings ("Learn more (verified):" and
    "Learn more (verified pointers):"), bullets at any indentation, and
    wrapped continuation lines, which are joined onto their bullet.
    """
    bullets: list[str] = []
    collecting = False
    for line in skill_md.splitlines():
        if _MARKER.search(line):
            collecting = True
            continue
        if not collecting:
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
        elif stripped == "":
            continue
        elif line.startswith((" ", "\t")) and bullets and not stripped.startswith("#"):
            bullets[-1] += " " + stripped
        else:
            collecting = False
    seen: set[str] = set()
    unique = []
    for b in bullets:
        if b not in seen:
            seen.add(b)
            unique.append(b)
    return unique


def reference_body(skill_md: str) -> str:
    bullets = extract_curated(skill_md)
    lines = [GENERATED_HEADER + "# References", ""]
    if bullets:
        lines += ["Learn more:", ""]
        lines += [f"- {b}" for b in bullets]
        lines.append("")
    else:
        lines += ["No curated external links for this skill yet.", ""]
    return "\n".join(lines).rstrip() + "\n"


def generate_references(skills_dir: Path) -> list[Path]:
    written = []
    for skill_dir in sorted(skills_dir.iterdir()):
        skill_md_path = skill_dir / "SKILL.md"
        if not skill_md_path.is_file():
            continue
        out = skill_dir / "references.md"
        out.write_text(
            reference_body(skill_md_path.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
        written.append(out)
    return written


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    written = generate_references(repo_root / "skills")
    print(f"wrote references.md for {len(written)} skills")


if __name__ == "__main__":
    main()
