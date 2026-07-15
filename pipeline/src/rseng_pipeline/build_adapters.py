"""Build every registered adapter target into dist/.

Usage: python -m rseng_pipeline.build_adapters [target ...]

With no arguments all targets build. dist/<target>/ is wiped and rebuilt
per target, so removed files prune automatically.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from . import targets  # noqa: F401  (importing registers TARGETS)
from .adapters import TARGETS, load_render_context, template_env
from .checks import check_target


def _structure_problems(dist_dir: Path, name: str, context: dict) -> list[str]:
    """Static per-target completeness: every skill, command and the
    self-check must actually land where that platform reads them.
    Guards the platforms with no CLI to behavior-test (copilot, cursor)."""
    n_skills = len(context["skills"])
    n_commands = len(context["commands"])
    target = dist_dir / name
    expected: dict[str, list[tuple[str, int]]] = {
        "codex": [
            ("skills/*/SKILL.md", n_skills),
            ("rseng-check/rseng_check.py", 1),
            ("rseng-check/phases.json", 1),
        ],
        "gemini": [
            ("skills/*/SKILL.md", n_skills),
            ("commands/*.toml", n_commands),
            ("rseng-check/rseng_check.py", 1),
        ],
        "copilot": [
            (".github/instructions/*.instructions.md", n_skills),
            (".github/skills/*/SKILL.md", n_skills),
            (".github/prompts/*.prompt.md", n_commands),
            (".github/rseng-check/rseng_check.py", 1),
        ],
        "cursor": [
            (".cursor/rules/*.mdc", n_skills + 1),
            (".cursor/commands/*.md", n_commands),
            (".cursor/skills/*/SKILL.md", n_skills),
            (".cursor/rseng-check/rseng_check.py", 1),
        ],
    }
    problems = []
    for pattern, count in expected.get(name, []):
        found = len(list(target.glob(pattern)))
        if found != count:
            problems.append(f"{name}: {pattern} has {found} files, expected {count}")
    if name == "cursor":
        rules = [
            p
            for p in target.glob(".cursor/rules/rseng-*.mdc")
            if p.name != "rseng-overview.mdc"
        ]
        missing = [
            p.name
            for p in rules
            if "Related skills" not in p.read_text(encoding="utf-8")
        ]
        if missing:
            problems.append(
                f"cursor: rules missing a Related skills block: {missing[:5]}"
            )
    return problems


def build(repo_root: Path, only: list[str] | None = None) -> dict[str, list[Path]]:
    names = only or sorted(TARGETS)
    unknown = [name for name in names if name not in TARGETS]
    if unknown:
        raise SystemExit(f"unknown target(s): {unknown}; known: {sorted(TARGETS)}")

    context = load_render_context(repo_root)
    env = template_env(repo_root)
    dist_dir = repo_root / "dist"

    results: dict[str, list[Path]] = {}
    problems: list[str] = []
    for name in names:
        target_dir = dist_dir / name
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True)
        results[name] = TARGETS[name](repo_root, env, context, target_dir)
        problems.extend(check_target(target_dir))
        problems.extend(_structure_problems(dist_dir, name, context))
    if problems:
        raise SystemExit("adapter checks failed:\n" + "\n".join(problems))
    return results


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    results = build(repo_root, sys.argv[1:] or None)
    if not results:
        print("no targets registered yet")
        return
    for name, files in results.items():
        print(f"{name}: {len(files)} files")


if __name__ == "__main__":
    main()
