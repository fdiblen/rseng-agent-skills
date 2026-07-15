"""Catalog of external skills and add-ons.

The catalog (catalog.yml at the repository root) records ONLINE links to
candidate skills, extensions and related standards. Nothing in it is
fetched automatically: a maintainer explicitly stages a pinned entry into
the git-ignored staging/ area, reviews the content, and only then vendors
the skill folders into skills/. `check` enforces catalog hygiene in CI
without touching the network.

Usage:
    python -m rseng_pipeline.catalog list
    python -m rseng_pipeline.catalog check
    python -m rseng_pipeline.catalog stage <name>
"""

from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path

import yaml

from .net import http_get as _get

KINDS = {"github", "website", "marketplace", "registry"}
STATUSES = {"proposed", "reviewed", "included"}
_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_GITHUB_RE = re.compile(r"^https://github\.com/([\w.-]+)/([\w.-]+?)/?$")
_SUSPECT_SUFFIXES = {".sh", ".bash", ".ps1", ".exe", ".bin", ".so", ".dylib", ".pyc"}


def load_catalog(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {
        "categories": list(data.get("categories") or []),
        "entries": list(data.get("entries") or []),
    }


def validate_catalog(catalog: dict) -> list[str]:
    problems: list[str] = []
    categories = set(catalog["categories"])
    seen: set[str] = set()
    for entry in catalog["entries"]:
        name = str(entry.get("name", ""))
        where = f"entry {name or '<unnamed>'}"
        if not _NAME_RE.match(name):
            problems.append(f"{where}: invalid name")
        if name in seen:
            problems.append(f"{where}: duplicate name")
        seen.add(name)
        if not str(entry.get("url", "")).startswith("https://"):
            problems.append(f"{where}: url must be https")
        if entry.get("kind") not in KINDS:
            problems.append(f"{where}: kind must be one of {sorted(KINDS)}")
        if entry.get("category") not in categories:
            problems.append(f"{where}: category not in catalog categories")
        if entry.get("status") not in STATUSES:
            problems.append(f"{where}: status must be one of {sorted(STATUSES)}")
        if entry.get("status") in {"reviewed", "included"}:
            review = entry.get("review") or {}
            if not review.get("by") or not review.get("date"):
                problems.append(
                    f"{where}: {entry['status']} needs review.by and review.date"
                )
            if entry.get("kind") == "github" and not _SHA_RE.match(
                str(entry.get("pin", ""))
            ):
                problems.append(f"{where}: github entries need a full commit pin")
    return problems


def check(repo_root: Path) -> list[str]:
    """Catalog hygiene for CI: valid entries, included content present."""
    catalog = load_catalog(repo_root / "catalog.yml")
    problems = validate_catalog(catalog)
    for entry in catalog["entries"]:
        if entry.get("status") != "included":
            continue
        for skill in entry.get("skills") or [entry.get("name")]:
            if not (repo_root / "skills" / str(skill) / "SKILL.md").is_file():
                problems.append(
                    f"entry {entry.get('name')}: included but skills/{skill}/SKILL.md missing"
                )
    return problems


def stage(repo_root: Path, name: str) -> Path:
    """Fetch ONE pinned github entry into staging/ for human review."""
    catalog = load_catalog(repo_root / "catalog.yml")
    entry = next((e for e in catalog["entries"] if e.get("name") == name), None)
    if entry is None:
        raise SystemExit(f"no catalog entry named {name!r}")
    if entry.get("kind") != "github":
        raise SystemExit(
            "only github entries can be staged; review others in the browser"
        )
    match = _GITHUB_RE.match(str(entry.get("url", "")))
    if not match:
        raise SystemExit(f"unsupported github url: {entry.get('url')}")
    pin = str(entry.get("pin", ""))
    if not _SHA_RE.match(pin):
        raise SystemExit("add a full 40-hex `pin:` commit to the entry before staging")

    owner, repo = match.groups()
    archive = _get(f"https://codeload.github.com/{owner}/{repo}/zip/{pin}")
    target = repo_root / "staging" / name
    target.mkdir(parents=True, exist_ok=True)
    skills_found: list[str] = []
    suspicious: list[str] = []
    total = 0
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        for info in bundle.infolist():
            if info.is_dir():
                continue
            rel = Path(*Path(info.filename).parts[1:])  # strip repo-pin prefix
            if rel.is_absolute() or ".." in rel.parts:
                continue  # zip-slip guard
            total += 1
            if rel.name == "SKILL.md":
                skills_found.append(str(rel.parent))
            if rel.suffix.lower() in _SUSPECT_SUFFIXES:
                suspicious.append(str(rel))
            out = target / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(bundle.read(info))

    report = target.parent / f"{name}.report.md"
    lines = [
        f"# Staging report: {name}",
        "",
        f"Source: {entry['url']} @ {pin[:8]}",
        f"Files extracted: {total}",
        "",
        "SKILL.md folders found:" if skills_found else "No SKILL.md folders found.",
        *[f"- {skill}" for skill in sorted(skills_found)],
        "",
    ]
    if suspicious:
        lines += [
            "REVIEW CAREFULLY - executable or binary files:",
            *[f"- {path}" for path in sorted(suspicious)[:50]],
            "",
        ]
    lines += [
        "Next: review the content, then vendor chosen skill folders into",
        "skills/, set the entry's status to included, list its `skills:`",
        "and record the review block. staging/ is git-ignored.",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main() -> None:
    import sys

    repo_root = Path(__file__).resolve().parents[3]
    command = sys.argv[1] if len(sys.argv) > 1 else "list"
    if command == "list":
        catalog = load_catalog(repo_root / "catalog.yml")
        for entry in catalog["entries"]:
            print(
                f"{entry.get('status', '?'):9s} {entry.get('category', '?'):17s} "
                f"{entry.get('name')}  {entry.get('url')}"
            )
    elif command == "check":
        problems = check(repo_root)
        for problem in problems:
            print(f"CATALOG: {problem}")
        if problems:
            raise SystemExit(1)
        print("catalog ok")
    elif command == "stage":
        report = stage(repo_root, sys.argv[2])
        print(f"staged; review report: {report}")
    else:
        raise SystemExit(f"unknown command {command!r}")


if __name__ == "__main__":
    main()
