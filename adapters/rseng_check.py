#!/usr/bin/env python3
"""rseng-agent-skills self-check for agents without a hook system.

Claude Code enforces the pack's practice mechanically through hooks;
other platforms (Codex, Gemini, Copilot, Cursor) ship this script
instead. Run it from the project root before declaring a coding task
complete and fix everything it reports. Stdlib only, no installation.

Checks: the practice artifact floor (README, LICENSE, CITATION.cff,
tests, environment declaration) and the phased practice
worklog (.rseng-agent-skills-coverage.md with Start / During / Finish /
Throughout sections covering every cluster in phases.json, each
recorded as 'applied: ...' or 'n/a: <reason>').
"""

import json
import pathlib
import re
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


def mentions(name, text):
    """Is this exact skill named in the text?

    Plain substring matching made one skill name a prefix of another:
    'rseng-data-management' sits inside 'rseng-data-management-plans', so
    dispositioning the plans skill silently dispositioned the other one too.
    \\b does not help - a hyphen is itself a word boundary - so the
    neighbours are excluded explicitly.
    """
    return re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", text) is not None


def _is_project_file(path: pathlib.Path, root: pathlib.Path) -> bool:
    """Does this path belong to the project, rather than to its tooling?

    Judged on the path RELATIVE to the project: an absolute path can pass
    through a dot-directory that has nothing to do with the project (a
    checkout under ~/.local, say) and that must not hide the whole tree.
    """
    parts = path.relative_to(root).parts
    # node_modules and site-packages are unambiguously other people's code.
    # "vendor" is not - plenty of projects keep their own source there, and
    # excluding it reported a confident clean pass on an unaudited tree.
    return not any(part.startswith(".") for part in parts) and not (
        {"node_modules", "site-packages"} & set(parts)
    )


CODE_GLOBS = ("*.py", "*.R", "*.jl", "*.js", "*.ts", "*.c", "*.cpp", "*.f90")
SOURCE_SUFFIXES = (
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
CFF_FIELDS = ("title", "authors", "version", "date-released", "license")
AGENT_DIRS = (".claude", ".agents", ".cursor", ".codex", ".gemini")


def artifact_floor(root, code, waived):
    """The artifacts a research project needs regardless of what it does."""
    missing = []
    present = [d for d in AGENT_DIRS if (root / d).is_dir()]
    if present:
        gi = root / ".gitignore"
        gi_text = (
            gi.read_text(encoding="utf-8", errors="replace") if gi.is_file() else ""
        )
        uncovered = [d for d in present if d not in gi_text]
        if uncovered:
            missing.append(
                ".gitignore missing the agent working directories present "
                f"here ({', '.join(uncovered)}) - add them plus .env and "
                ".rseng-agent-skills-* session records and .rseng-backup-* directories"
            )

    def require(key, ok, message):
        if ok or key in waived:
            return
        missing.append(message)

    require(
        "README", bool(list(root.glob("README*"))), "README with purpose and how-to-run"
    )
    require(
        "LICENSE",
        bool(list(root.glob("LICENSE*"))),
        "LICENSE (unlicensed code legally blocks all reuse)",
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
            for field in CFF_FIELDS
            if not any(line.startswith(field + ":") for line in text.splitlines())
        ]
        if absent:
            missing.append(f"CITATION.cff fields: {', '.join(absent)}")

    # Filtered like the code scan: a dependency's own test files under
    # .venv/ used to satisfy this, so a project with no tests of its own
    # was told its practice artifacts were complete.
    tests = [p for p in root.rglob("test_*.py") if _is_project_file(p, root)] + [
        p for p in root.rglob("tests") if p.is_dir() and _is_project_file(p, root)
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
    return missing


def signal_gaps(root, rules, text):
    """Project contents that imply a skill require that skill dispositioned."""
    missing = []
    all_files = [
        p for p in root.rglob("*") if p.is_file() and _is_project_file(p, root)
    ][:4000]
    sources = [p for p in all_files if p.suffix in SOURCE_SUFFIXES]
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
            if not mentions(skill, text):
                missing.append(
                    f"{rule['name']} present ({evidence}) but {skill} has "
                    "no coverage entry - apply it or record "
                    f"'n/a: {skill} - <reason>'"
                )
    return missing


def phase_coverage(phases, text):
    """Every skill dispositioned, and every phase section present."""
    missing = []
    inventory = sorted(
        {s for cl in phases.values() for skills in cl.values() for s in skills}
    )
    absent = [s for s in inventory if not mentions(s, text)]
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
    return missing


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
    # A checker that cannot find its own data must not report success:
    # without phases.json the whole skill inventory and every cluster check
    # iterate over nothing, and without signals.json all the relevance rules
    # are skipped - and the script still printed "complete".
    phases_file = here / "phases.json"
    signals_file = here / "signals.json"
    no_data = [f.name for f in (phases_file, signals_file) if not f.is_file()]
    if no_data:
        print(
            f"rseng-check: cannot run - {', '.join(no_data)} missing from "
            f"{here}. This copy of the check is incomplete; reinstall the "
            "pack rather than trusting its result."
        )
        return 2
    phases = json.loads(phases_file.read_text(encoding="utf-8"))
    rules = json.loads(signals_file.read_text(encoding="utf-8"))

    code = [
        p for ext in CODE_GLOBS for p in root.rglob(ext) if _is_project_file(p, root)
    ]
    if not code:
        print("rseng-check: no code files found; nothing to audit")
        return 0

    coverage = root / ".rseng-agent-skills-coverage.md"
    text = (
        coverage.read_text(encoding="utf-8", errors="replace").lower()
        if coverage.is_file()
        else ""
    )

    missing = artifact_floor(root, code, _waivers(root))
    missing += signal_gaps(root, rules, text)
    missing += phase_coverage(phases, text)

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
