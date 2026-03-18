"""Classify upstream RSQKit changes against the pinned manifest.

Levels (see the sync strategy in the implementation plan):

- L1 references-only: registry data changed (tool descriptions and other
  _data values). Regeneration is safe; the sync PR can auto-merge.
- L2 body-review: content of a mapped page changed; the skills built on
  it need a human look at their hand-authored bodies.
- L3 structural: pages appeared, disappeared or were renamed, or a
  registry's structure changed; taxonomy.yml needs a human update.

Usage: python -m rseng_pipeline.sync_classifier [ref]   (default: main)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

import frontmatter

from .fetcher import RAW_BASE, TREE_API, UpstreamPin, _get, load_pin, selects
from .lock_manifest import read_lock_manifest
from .references import load_taxonomy, skill_page_ids


@dataclass
class PageChange:
    path: str
    page_id: str
    skills: list[str]


@dataclass
class ChangeReport:
    old_commit: str
    new_commit: str
    added: list[PageChange] = field(default_factory=list)
    removed: list[PageChange] = field(default_factory=list)
    modified_pages: list[PageChange] = field(default_factory=list)
    modified_data: list[str] = field(default_factory=list)
    renames: list[tuple[str, str]] = field(default_factory=list)  # old->new id

    @property
    def level(self) -> str:
        if self.added or self.removed or self.renames:
            return "L3"
        if self.modified_pages:
            return "L2"
        if self.modified_data:
            return "L1"
        return "none"

    @property
    def affected_skills(self) -> list[str]:
        skills: set[str] = set()
        for group in (self.added, self.removed, self.modified_pages):
            for change in group:
                skills.update(change.skills)
        return sorted(skills)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _page_id_of(path: str, blob: bytes) -> str:
    meta = frontmatter.loads(blob.decode("utf-8", errors="replace")).metadata
    return str(meta.get("page_id") or Path(path).stem)


def _skills_for(page_id: str, taxonomy: dict) -> list[str]:
    return sorted(
        name for name, entry in taxonomy.items() if page_id in skill_page_ids(entry)
    )


def fetch_upstream_state(
    pin: UpstreamPin, ref: str = "main"
) -> tuple[str, dict[str, bytes]]:
    """Resolve a ref and download every selected source file at it."""
    tree = json.loads(_get(TREE_API.format(repo=pin.repo, commit=ref)))
    commit = tree["sha"]
    blobs: dict[str, bytes] = {}
    for entry in tree["tree"]:
        if entry["type"] == "blob" and selects(pin, entry["path"]):
            blobs[entry["path"]] = _get(
                f"{RAW_BASE}/{pin.repo}/{commit}/{entry['path']}"
            )
    return commit, blobs


def classify(
    pipeline_dir: Path,
    taxonomy_path: Path,
    new_commit: str,
    new_blobs: dict[str, bytes],
) -> ChangeReport:
    """Diff new upstream content against the committed lock manifest."""
    manifest = read_lock_manifest(pipeline_dir)
    taxonomy = load_taxonomy(taxonomy_path)
    old_files: dict[str, str] = manifest["files"]
    cache_dir = pipeline_dir / "cache"

    report = ChangeReport(old_commit=manifest["commit"], new_commit=new_commit)

    def old_page_id(path: str) -> str:
        cached = cache_dir / path
        if cached.is_file():
            return _page_id_of(path, cached.read_bytes())
        return Path(path).stem

    for path in sorted(set(old_files) | set(new_blobs)):
        is_page = path.startswith("pages/")
        old_hash = old_files.get(path)
        new_blob = new_blobs.get(path)

        if old_hash and new_blob is None:
            if is_page:
                page_id = old_page_id(path)
                report.removed.append(
                    PageChange(path, page_id, _skills_for(page_id, taxonomy))
                )
            else:
                report.modified_data.append(f"{path} (removed)")
        elif old_hash is None and new_blob is not None:
            if is_page:
                page_id = _page_id_of(path, new_blob)
                report.added.append(
                    PageChange(path, page_id, _skills_for(page_id, taxonomy))
                )
            else:
                report.modified_data.append(f"{path} (added)")
        elif old_hash and new_blob is not None and _sha256(new_blob) != old_hash:
            if is_page:
                page_id = _page_id_of(path, new_blob)
                report.modified_pages.append(
                    PageChange(path, page_id, _skills_for(page_id, taxonomy))
                )
            else:
                report.modified_data.append(path)

    # A removed and an added page sharing a page_id (or the added file's
    # frontmatter carrying a removed page's id) is a rename, not churn.
    removed_ids = {change.page_id: change for change in report.removed}
    for added in list(report.added):
        if added.page_id in removed_ids:
            report.renames.append((added.page_id, added.page_id))
            report.added.remove(added)
            report.removed.remove(removed_ids[added.page_id])
    return report


def render_report(report: ChangeReport) -> str:
    lines = [
        f"# Upstream change report ({report.level})",
        "",
        f"Pinned: {report.old_commit[:8]} -> upstream: {report.new_commit[:8]}",
        "",
    ]
    if report.level == "none":
        lines.append("No changes in the pinned source set.")
        return "\n".join(lines) + "\n"

    def section(title: str, items: list[str]) -> None:
        if items:
            lines.append(f"## {title}")
            lines.append("")
            lines.extend(f"- {item}" for item in items)
            lines.append("")

    section(
        "L3: added pages (map in taxonomy.yml)",
        [f"{c.path} (page_id `{c.page_id}`)" for c in report.added],
    )
    section(
        "L3: removed pages (prune + review citing skills)",
        [
            f"{c.path} (page_id `{c.page_id}`; review: {', '.join(c.skills) or 'unmapped'})"
            for c in report.removed
        ],
    )
    section(
        "L3: renamed page_ids",
        [f"`{old}` -> `{new}`" for old, new in report.renames],
    )
    section(
        "L2: modified pages (review skill bodies)",
        [
            f"{c.path} (skills: {', '.join(c.skills) or 'unmapped'})"
            for c in report.modified_pages
        ],
    )
    section("L1: registry/data changes (regeneration is safe)", report.modified_data)
    if report.affected_skills:
        lines.append(f"Affected skills: {', '.join(report.affected_skills)}")
        lines.append("")
    return "\n".join(lines) + "\n"


def triage_suggestions(
    pipeline_dir: Path,
    taxonomy_path: Path,
    report: ChangeReport,
    new_blobs: dict[str, bytes],
) -> str:
    """Render taxonomy suggestions for the report's added pages."""
    from .parser import load_pages
    from .triage import render_suggestions, suggest_mapping

    if not report.added:
        return ""
    taxonomy = load_taxonomy(taxonomy_path)
    known_keywords = {
        page_id: {word for kw in rec.keywords for word in kw.lower().split()}
        for page_id, rec in load_pages(pipeline_dir / "cache").items()
    }
    suggestions = [
        suggest_mapping(change.path, new_blobs[change.path], taxonomy, known_keywords)
        for change in report.added
    ]
    return render_suggestions(suggestions)


def main() -> None:
    import sys

    pipeline_dir = Path(__file__).resolve().parents[2]
    repo_root = pipeline_dir.parent
    taxonomy_path = repo_root / "skills" / "taxonomy.yml"
    ref = sys.argv[1] if len(sys.argv) > 1 else "main"
    pin = load_pin(pipeline_dir / "upstream.lock")
    commit, blobs = fetch_upstream_state(pin, ref)
    report = classify(pipeline_dir, taxonomy_path, commit, blobs)
    output = render_report(report) + triage_suggestions(
        pipeline_dir, taxonomy_path, report, blobs
    )
    print(output, end="")
    (pipeline_dir / "build").mkdir(exist_ok=True)
    (pipeline_dir / "build" / "change-report.md").write_text(output)
    print(f"level={report.level}", file=sys.stderr)


if __name__ == "__main__":
    main()
