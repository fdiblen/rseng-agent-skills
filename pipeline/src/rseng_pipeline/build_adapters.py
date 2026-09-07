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

#: Credit and licence files that travel with the content into every bundle.
#: Every bundle ships MIT code (rseng-check) alongside CC-BY content,
#: so both licence texts travel with it, not just the content one.
NOTICE_FILES = ("ATTRIBUTION.md", "NOTICE", "LICENSE", "LICENSE-content")


def _structure_problems(dist_dir: Path, name: str, context: dict) -> list[str]:
    """Static per-target completeness: every skill, command and the
    self-check must actually land where that platform reads them.
    Guards the platforms with no CLI to behavior-test (copilot, cursor)."""
    n_skills = len(context["skills"])
    n_commands = len(context["commands"])
    target = dist_dir / name
    n_cmd_skills = n_commands - 1  # rseng-panel stays Claude-only
    # The skill bodies are CC-BY-4.0 adaptations. A bundle that carries
    # them without the credit and the licence text cannot be
    # redistributed, so every target is required to ship all four.
    # Spelled out rather than derived from NOTICE_FILES: that constant
    # is what the copy loop below iterates, so checking against it
    # checked the writer against itself - dropping LICENSE-content
    # from every bundle built green.
    notices = [
        (".agents/ATTRIBUTION.md", 1),
        (".agents/NOTICE", 1),
        (".agents/LICENSE", 1),
        (".agents/LICENSE-content", 1),
    ]
    unified = notices + [
        (".agents/skills/*/SKILL.md", n_skills + n_cmd_skills),
        (".agents/skills/rseng-check/agents/openai.yaml", 1),
    ]
    expected: dict[str, list[tuple[str, int]]] = {
        # The hook layer is the reason hook_wiring.py exists, and it had
        # no expectations at all: making write_hooks return [] dropped
        # twelve files from codex and gemini and still built green.
        "codex": unified
        + [
            ("AGENTS.md", 1),
            ("rseng-check/rseng_check.py", 1),
            ("rseng-check/phases.json", 1),
            ("rseng-check/signals.json", 1),
            ("rseng-check/phases.json", 1),
            ("rseng-check/signals.json", 1),
            (".codex/hooks.json", 1),
            (".codex/rseng/gate.py", 1),
            (".codex/rseng/quality_check.py", 1),
            (".codex/rseng/session_start.py", 1),
            (".codex/rseng/phases.json", 1),
            (".codex/rseng/signals.json", 1),
        ],
        "cursor": unified
        + [
            (".cursor/rules/*.mdc", 1),
            (".cursor/rseng-check/rseng_check.py", 1),
            (".cursor/rseng-check/phases.json", 1),
            (".cursor/rseng-check/signals.json", 1),
        ],
        "copilot": unified
        + [
            (".github/copilot-instructions.md", 1),
            (".github/rseng-check/rseng_check.py", 1),
            (".github/rseng-check/phases.json", 1),
            (".github/rseng-check/signals.json", 1),
        ],
        "gemini": unified
        + [
            ("GEMINI.md", 1),
            ("rseng-check/rseng_check.py", 1),
            ("rseng-check/phases.json", 1),
            ("rseng-check/signals.json", 1),
            (".gemini/settings.json", 1),
            (".gemini/rseng/gate.py", 1),
            (".gemini/rseng/quality_check.py", 1),
            (".gemini/rseng/session_start.py", 1),
            (".gemini/rseng/phases.json", 1),
            (".gemini/rseng/signals.json", 1),
        ],
        "antigravity": unified
        + [
            ("GEMINI.md", 1),
            ("AGENTS.md", 1),
            ("rseng-check/rseng_check.py", 1),
        ],
        # Not `unified`: an extension's skills live in skills/, its hooks
        # in hooks/hooks.json, and without gemini-extension.json in the
        # root Gemini CLI never loads any of it.
        "gemini-extension": notices
        + [
            ("gemini-extension.json", 1),
            ("GEMINI.md", 1),
            ("skills/*/SKILL.md", n_skills + n_cmd_skills),
            ("skills/rseng-check/agents/openai.yaml", 1),
            ("hooks/hooks.json", 1),
            ("rseng/gate.py", 1),
            ("rseng-check/rseng_check.py", 1),
        ],
    }
    if name not in expected:
        # A target with no entry checked nothing at all, so a new adapter
        # that shipped an empty directory built green.
        return [f"{name}: no structure expectations defined for this target"]
    problems = []
    for pattern, count in expected[name]:
        found = len(list(target.glob(pattern)))
        if found != count:
            problems.append(f"{name}: {pattern} has {found} files, expected {count}")
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
        for notice in NOTICE_FILES:
            # Beside the skills, not at the bundle root: gemini and
            # antigravity copy the whole tree into the project root, and a
            # root-level NOTICE or LICENSE-content reads as the user's own.
            dest = target_dir / ".agents" / notice
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(repo_root / notice, dest)
            results[name].append(dest)
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
