#!/usr/bin/env python3
"""rseng-agent-skills self-check for agents without a hook system.

Claude Code enforces the pack's practice mechanically through hooks;
other platforms (Codex, Gemini, Copilot, Cursor) ship this script
instead. Run it from the project root before declaring a coding task
complete and fix everything it reports. Stdlib only, no installation.

Checks: the practice artifact floor (README, LICENSE, aidecl.yaml,
CITATION.cff, tests, environment declaration) and the phased practice
worklog (.rseng-agent-skills-coverage.md with Start / During / Finish /
Throughout sections covering every cluster in phases.json, each
recorded as 'applied: ...' or 'n/a: <reason>').
"""

import json
import pathlib
import sys


def main() -> int:
    root = pathlib.Path(".")
    here = pathlib.Path(__file__).resolve().parent
    phases_file = here / "phases.json"
    phases = (
        json.loads(phases_file.read_text(encoding="utf-8"))
        if phases_file.is_file()
        else {}
    )

    code = [
        p
        for ext in ("*.py", "*.R", "*.jl", "*.js", "*.ts", "*.c", "*.cpp", "*.f90")
        for p in root.rglob(ext)
        if not any(part.startswith(".") for part in p.parts)
        and "node_modules" not in p.parts
    ]
    if not code:
        print("rseng-check: no code files found; nothing to audit")
        return 0

    missing = []
    if not list(root.glob("README*")):
        missing.append("README with purpose and how-to-run")
    if not list(root.glob("LICENSE*")):
        missing.append("LICENSE (unlicensed code legally blocks all reuse)")
    if not (root / "aidecl.yaml").is_file():
        missing.append("aidecl.yaml AI usage declaration")
    if not (root / "CITATION.cff").is_file():
        missing.append("CITATION.cff citation metadata")
    tests = [p for p in root.rglob("test_*.py")] + [
        p for p in root.rglob("tests") if p.is_dir()
    ]
    if not tests:
        missing.append("tests (at least a smoke/reference-case check)")
    if not (
        list(root.glob("pyproject.toml"))
        or list(root.glob("uv.lock"))
        or list(root.glob("requirements*.txt"))
        or list(root.glob("environment*.y*ml"))
        or any(
            "# /// script" in p.read_text(encoding="utf-8", errors="ignore")
            for p in code[:10]
            if p.suffix == ".py"
        )
    ):
        missing.append("environment/dependency declaration (uv + pyproject or PEP 723)")

    coverage = root / ".rseng-agent-skills-coverage.md"
    text = coverage.read_text(encoding="utf-8").lower() if coverage.is_file() else ""
    for phase, clusters in phases.items():
        if f"## {phase.lower()}" not in text:
            missing.append(
                f".rseng-agent-skills-coverage.md '## {phase}' section covering: "
                + "; ".join(clusters)
            )
            continue
        for cluster in clusters:
            pos = text.find(cluster.lower())
            if pos < 0:
                missing.append(
                    f"coverage entry for {phase} / {cluster} "
                    "('applied: <skills and decisions>' or 'n/a: <reason>')"
                )
                continue
            window = text[pos : pos + 400]
            if "applied" not in window and "n/a" not in window:
                missing.append(
                    f"{phase} / {cluster}: add 'applied: ...' or 'n/a: <reason>'"
                )

    if missing:
        print(
            "rseng-check: this project is missing practice artifacts. "
            "Add each item, or record briefly why it does not apply:"
        )
        for item in missing:
            print(f"- {item}")
        return 1
    print("rseng-check: practice artifacts and phased coverage complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
