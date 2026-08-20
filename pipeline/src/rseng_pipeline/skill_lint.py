"""Frontmatter lint for the skill sources.

`skills-ref validate` checks the Agent Skills spec shape; this lint
adds the repo's own floor on top: the frontmatter name must match the
skill's directory, the description must stay within the spec's
1024-character cap (the token budget is a separate, tighter gate),
and the fields every skill in this pack carries (license,
metadata.version) must be present and well-formed. Runs in CI so a
bad edit fails the build naming the skill, not a user session.

Usage:
    python -m rseng_pipeline.skill_lint
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

DESCRIPTION_CHAR_CAP = 1024
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_CHAR_CAP = 64
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
KNOWN_KEYS = {
    "name",
    "description",
    "license",
    "metadata",
    "allowed-tools",
    "compatibility",
}


def lint_skill(skill_md: Path) -> list[str]:
    """Problems for one SKILL.md; empty list means clean."""
    directory = skill_md.parent.name
    text = skill_md.read_text(encoding="utf-8")
    fm = re.match(r"(?s)^---\n(.*?)\n---\n", text)
    if not fm:
        return [f"{directory}: no frontmatter block"]
    try:
        meta = yaml.safe_load(fm.group(1))
    except yaml.YAMLError as exc:
        return [f"{directory}: frontmatter is not valid YAML ({exc})"]
    if not isinstance(meta, dict):
        return [f"{directory}: frontmatter is not a mapping"]

    out = []
    name = meta.get("name")
    if not name:
        out.append(f"{directory}: missing required field 'name'")
    else:
        if name != directory:
            out.append(
                f"{directory}: frontmatter name '{name}' does not match "
                "the directory name"
            )
        if not NAME_PATTERN.match(str(name)):
            out.append(
                f"{directory}: name must be lowercase letters, digits "
                "and single hyphens"
            )
        if "--" in str(name):
            out.append(f"{directory}: name contains consecutive hyphens")
        if len(str(name)) > NAME_CHAR_CAP:
            out.append(f"{directory}: name exceeds {NAME_CHAR_CAP} characters")

    description = meta.get("description")
    if not description or not str(description).strip():
        out.append(f"{directory}: missing required field 'description'")
    elif len(str(description)) > DESCRIPTION_CHAR_CAP:
        out.append(
            f"{directory}: description {len(str(description))} chars "
            f"(spec cap {DESCRIPTION_CHAR_CAP})"
        )

    if not meta.get("license"):
        out.append(f"{directory}: missing 'license'")

    md = meta.get("metadata") or {}
    for key, value in md.items():
        if not isinstance(value, str):
            out.append(
                f"{directory}: metadata.{key} is "
                f"{type(value).__name__} (spec requires string values)"
            )

    version = md.get("version")
    if not version:
        out.append(f"{directory}: missing 'metadata.version'")
    elif not VERSION_PATTERN.match(str(version)):
        out.append(
            f"{directory}: metadata.version '{version}' is not MAJOR.MINOR.PATCH"
        )

    unknown = set(meta) - KNOWN_KEYS
    if unknown:
        out.append(
            f"{directory}: unknown frontmatter keys: {', '.join(sorted(unknown))}"
        )
    return out


def lint_all(repo_root: Path) -> list[str]:
    skill_files = sorted(repo_root.glob("skills/*/SKILL.md"))
    problems = []
    for skill_md in skill_files:
        problems += lint_skill(skill_md)
    if not skill_files:
        problems.append("no skills found under skills/")
    return problems


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    problems = lint_all(repo_root)
    count = len(list(repo_root.glob("skills/*/SKILL.md")))
    if problems:
        print(f"skill lint: {len(problems)} problem(s) across {count} skills")
        for p in problems:
            print(f"- {p}")
        raise SystemExit(1)
    print(f"skill lint: {count} skills clean")


if __name__ == "__main__":
    main()
