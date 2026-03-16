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
        problems.extend(check_target(target_dir, commit=context["upstream"]["commit"]))
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
