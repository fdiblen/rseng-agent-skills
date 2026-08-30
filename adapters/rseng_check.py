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

WAIVER_FILE = ".rseng-check-waivers"


def _waivers(root: pathlib.Path) -> dict[str, str]:
    """Artifacts this project has deliberately opted out of, with reasons.

    The check tells you to add each missing item "or record briefly why it
    does not apply". Without somewhere to record that, the only way to make
    the check pass was to comply - so a considered exception looked exactly
    like neglect. One `artifact: reason` per line; blank lines and # ignored.
    """
    path = root / WAIVER_FILE
    if not path.is_file():
        return {}
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, reason = line.partition(":")
        if reason.strip():
            out[key.strip()] = reason.strip()
    return out


def main() -> int:
    # Audit the directory named on the command line, or the current one.
    # This used to be hardcoded to ".", so passing a path was accepted in
    # silence and the wrong project was audited with a confident verdict.
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if len(args) > 1:
        print(f"rseng-check: expected at most one path, got {len(args)}")
        return 2
    # resolve(): a relative path like ../project keeps ".." in every
    # rglob result, and the hidden-file filter below drops any part starting
    # with "." - so the audit found zero files and reported "nothing to
    # audit" for a project full of code.
    root = pathlib.Path(args[0] if args else ".").resolve()
    if not root.is_dir():
        print(f"rseng-check: not a directory: {args[0] if args else '.'}")
        return 2
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
    waived = _waivers(root)
    agent_dirs = (".claude", ".agents", ".cursor", ".codex", ".gemini")
    present = [d for d in agent_dirs if (root / d).is_dir()]
    if present:
        gi = root / ".gitignore"
        gi_text = gi.read_text(encoding="utf-8") if gi.is_file() else ""
        uncovered = [d for d in present if d not in gi_text]
        if uncovered:
            missing.append(
                ".gitignore missing the agent working directories present "
                f"here ({', '.join(uncovered)}) - add them plus .env and "
                ".rseng-agent-skills-* session records"
            )

    def require(key: str, ok: bool, message: str) -> None:
        if ok or key in waived:
            return
        missing.append(message)

    require(
        "README",
        bool(list(root.glob("README*"))),
        "README with purpose and how-to-run",
    )
    require(
        "LICENSE",
        bool(list(root.glob("LICENSE*"))),
        "LICENSE (unlicensed code legally blocks all reuse)",
    )
    require(
        "aidecl.yaml",
        (root / "aidecl.yaml").is_file(),
        "aidecl.yaml AI usage declaration",
    )
    citation = root / "CITATION.cff"
    if not citation.is_file():
        missing.append("CITATION.cff citation metadata")
    else:
        # A CITATION.cff that exists but omits half its fields still cites
        # badly. Checked by prefix rather than parsed: this script is stdlib
        # only, and PyYAML is not guaranteed in the project being checked.
        text = citation.read_text(encoding="utf-8", errors="ignore")
        absent = [
            field
            for field in ("title", "authors", "version", "date-released", "license")
            if not any(line.startswith(field + ":") for line in text.splitlines())
        ]
        if absent:
            missing.append(f"CITATION.cff fields: {', '.join(absent)}")
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

    # Relevance signals: project contents that imply a skill require
    # that skill dispositioned (applied or reasoned n/a) in the worklog.
    import re

    signals_file = here / "signals.json"
    if signals_file.is_file():
        rules = json.loads(signals_file.read_text(encoding="utf-8"))
        all_files = [
            p
            for p in root.rglob("*")
            if p.is_file()
            and not any(
                part.startswith(".") or part == "node_modules" for part in p.parts
            )
        ][:4000]
        sources = [
            p
            for p in all_files
            if p.suffix
            in (
                ".py",
                ".R",
                ".jl",
                ".sh",
                ".ipynb",
                ".c",
                ".h",
                ".cpp",
                ".cu",
                ".cuh",
                ".f",
                ".f90",
                ".F90",
            )
        ]
        for rule in rules:
            evidence = next(
                (
                    str(p)
                    for pattern in rule.get("patterns", [])
                    for p in all_files
                    if p.match(pattern)
                ),
                None,
            )
            if evidence is None:
                for regex in rule.get("content", []):
                    pat = re.compile(regex)
                    hit = next(
                        (
                            p
                            for p in sources[:60]
                            if pat.search(
                                p.read_text(encoding="utf-8", errors="ignore")[:200_000]
                            )
                        ),
                        None,
                    )
                    if hit:
                        evidence = str(hit)
                        break
            if evidence is None:
                continue
            for skill in rule["skills"]:
                if skill not in text:
                    missing.append(
                        f"{rule['name']} present ({evidence}) but {skill} has "
                        "no coverage entry - apply it or record "
                        f"'n/a: {skill} - <reason>'"
                    )

    # Full inventory: every skill in the pack gets a disposition.
    inventory = sorted(
        {s for cl in phases.values() for skills in cl.values() for s in skills}
    )
    absent = [s for s in inventory if s not in text]
    if absent:
        shown = ", ".join(absent[:12]) + (
            f" and {len(absent) - 12} more" if len(absent) > 12 else ""
        )
        missing.append(
            f"{len(absent)} skills lack a disposition in the coverage "
            f"worklog (applied or 'n/a: <reason>'): {shown}"
        )

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
