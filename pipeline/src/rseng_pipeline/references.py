"""Generate each skill's references/ folder from the build artifacts.

For every skill in the taxonomy this writes:

- references/pages/<page_id>.md - the cleaned fragment for each mapped
  page (tasks, concepts and roles alike)
- references/tools.md - the registry tools referenced by those pages
- references/learn-more.md - verified external and curated pointers

All outputs carry a generated-file header; the folder is wiped and
rebuilt on every run so removed upstream pages prune automatically.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml

GENERATED_HEADER = (
    "<!-- Generated file - do not edit. Rebuilt by the rseng-agent-skills\n"
    "     pipeline from RSQKit content; see pipeline/upstream.lock. -->\n\n"
)


def load_taxonomy(path: Path) -> dict[str, dict]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))["skills"]


def skill_page_ids(entry: dict) -> list[str]:
    return (
        list(entry.get("pages") or [])
        + list(entry.get("concept_pages") or [])
        + list(entry.get("role_pages") or [])
    )


def _tools_markdown(page_ids: list[str], content: dict) -> str:
    tool_ids = sorted(
        {
            ref
            for page_id in page_ids
            for ref in content["pages"].get(page_id, {}).get("tool_refs", [])
        }
    )
    lines = [GENERATED_HEADER + "# Tools referenced by this skill\n"]
    for tool_id in tool_ids:
        tool = content["tools"].get(tool_id)
        if tool is None or not tool["url"]:
            continue
        lines.append(f"- [{tool['name']}]({tool['url']}) - {tool['description']}")
    return "\n".join(lines) + "\n"


def _learn_more_markdown(page_ids: list[str], content: dict) -> str:
    lines = [GENERATED_HEADER + "# Learn more\n"]
    seen: set[str] = set()

    curated = []
    for page_id in page_ids:
        page = content["pages"].get(page_id)
        if page is None:
            continue
        for source in page["learn_more"]["curated"]:
            if source["url"] not in seen:
                seen.add(source["url"])
                curated.append(f"- [{source['label']}]({source['url']})")
    if curated:
        lines.append("## Training and courses\n")
        lines.extend(curated)
        lines.append("")

    for page_id in page_ids:
        page = content["pages"].get(page_id)
        if page is None:
            continue
        urls = [
            url
            for url in (page["learn_more"]["training"] + page["learn_more"]["external"])
            if url not in seen
        ]
        if not urls:
            continue
        lines.append(f"## From {page['title']} ({page['rsqkit_url']})\n")
        for url in urls:
            seen.add(url)
            lines.append(f"- {url}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _indicators_markdown(page_ids: list[str], content: dict) -> str:
    """Checklist of the indicators referenced by this skill's pages.

    The upstream registry defines no per-tier priority levels, so the
    checklist is grouped by quality dimension; agents judge applicability
    by software tier (see the rseng-quality-framework skill).
    """
    referencing: dict[str, list[str]] = {}
    for page_id in page_ids:
        page = content["pages"].get(page_id, {})
        for abbr in page.get("quality_indicators", []):
            referencing.setdefault(abbr, []).append(page_id)

    # The router skill maps no task pages; it gets the full registry.
    abbrs = referencing or {abbr: [] for abbr in content["indicators"]}

    by_dimension: dict[str, list[str]] = {}
    for abbr in sorted(abbrs):
        indicator = content["indicators"].get(abbr)
        if indicator is None:
            continue  # page references an id missing from the registry
        for dim in indicator["dimensions"] or ("unmapped",):
            by_dimension.setdefault(dim, []).append(abbr)

    lines = [GENERATED_HEADER + "# Quality indicator checklist\n"]
    lines.append(
        "Check each indicator that applies; judge applicability by the\n"
        "software's tier (analysis code, prototype tool, infrastructure).\n"
    )
    for dim in sorted(by_dimension):
        dimension = content["dimensions"].get(dim)
        title = dimension["name"] if dimension else dim
        lines.append(f"## {title}\n")
        for abbr in by_dimension[dim]:
            indicator = content["indicators"][abbr]
            lines.append(f"- [ ] {indicator['name']} (`{abbr}`)")
            if indicator["description"]:
                lines.append(f"      {indicator['description']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def generate_references(
    skills_dir: Path, taxonomy_path: Path, build_dir: Path
) -> list[Path]:
    """Write references/ for every skill; returns the folders written."""
    taxonomy = load_taxonomy(taxonomy_path)
    content = json.loads((build_dir / "content.json").read_text(encoding="utf-8"))
    fragments_dir = build_dir / "fragments"
    written = []

    for skill_name, entry in taxonomy.items():
        page_ids = skill_page_ids(entry)
        refs_dir = skills_dir / skill_name / "references"
        if refs_dir.exists():
            shutil.rmtree(refs_dir)
        pages_dir = refs_dir / "pages"
        pages_dir.mkdir(parents=True)

        for page_id in page_ids:
            fragment = fragments_dir / f"{page_id}.md"
            if not fragment.is_file():
                raise FileNotFoundError(
                    f"{skill_name}: no fragment for page_id {page_id!r}"
                )
            shutil.copyfile(fragment, pages_dir / f"{page_id}.md")

        (refs_dir / "tools.md").write_text(
            _tools_markdown(page_ids, content), encoding="utf-8"
        )
        (refs_dir / "learn-more.md").write_text(
            _learn_more_markdown(page_ids, content), encoding="utf-8"
        )
        (refs_dir / "indicators.md").write_text(
            _indicators_markdown(page_ids, content), encoding="utf-8"
        )
        written.append(refs_dir)
    return written


def main() -> None:
    pipeline_dir = Path(__file__).resolve().parents[2]
    repo_root = pipeline_dir.parent
    from .extension import extension_dir

    written = generate_references(
        repo_root / "skills",
        extension_dir(repo_root) / "taxonomy.yml",
        pipeline_dir / "build",
    )
    print(f"wrote references for {len(written)} skills")


if __name__ == "__main__":
    main()
