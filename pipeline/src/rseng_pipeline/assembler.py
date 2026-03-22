"""Assemble the pipeline build artifacts.

Reads the verified cache plus the data files and emits:

- build/content.json - every page record (cleaned body excluded), registry
  lookups, learn-more lists and provenance (upstream commit, page URL).
- build/fragments/<page_id>.md - cleaned markdown per page, each with a
  generated-file header carrying source path, upstream commit and license.

Everything under build/ is generated; nothing there is hand-edited.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .cleaner import clean_body
from .source import load_source
from .fetcher import UpstreamPin, load_pin, verify_cache
from .learn_more import collect_all, load_curated, merge_curated
from .parser import extract_tool_refs, load_pages
from .registry import (
    load_contributors,
    load_dimensions,
    load_indicators,
    load_tools,
)

FRAGMENT_HEADER = (
    "<!-- Generated file - do not edit.\n"
    "     Source: {source} @ {commit}\n"
    "     From {title} ({url}),\n"
    "     {license}. DOI: {doi} -->\n\n"
)


def _page_slug(record) -> str:
    """Site permalinks derive from the source FILENAME, not the page_id
    (they differ for three pages at the pinned commit)."""
    return Path(record.source_path).stem


def _page_entry(record, learn_more, base_url: str) -> dict:
    return {
        "page_id": record.page_id,
        "title": record.title,
        "description": record.description,
        "keywords": record.keywords,
        "contributors": record.contributors,
        "related_pages": record.related_pages,
        "quality_indicators": record.quality_indicators,
        "child_pages": record.child_pages,
        "source_path": record.source_path,
        "rsqkit_url": f"{base_url}/{_page_slug(record)}",
        # From the raw body: cleaning rewrites tool tags into plain links.
        "tool_refs": extract_tool_refs(record.body),
        "learn_more": {
            "external": list(learn_more.external),
            "training": list(learn_more.training),
            "curated": [asdict(source) for source in learn_more.curated],
        },
    }


def assemble(
    pipeline_dir: Path,
    build_dir: Path | None = None,
    pin: UpstreamPin | None = None,
) -> Path:
    """Build content.json and fragments from an already-fetched cache."""
    source = load_source(pipeline_dir.parent)
    cache_dir = pipeline_dir / "cache"
    data_dir = source.dir / "data"
    build_dir = build_dir or pipeline_dir / "build"
    pin = pin or load_pin(source.dir / "upstream.lock")

    problems = verify_cache(cache_dir)
    if problems:
        raise RuntimeError(f"cache not usable: {problems}")

    pages = load_pages(cache_dir)
    tools = load_tools(cache_dir / "_data/tool_and_resource_list.yml")
    contributors = load_contributors(cache_dir / "_data/CONTRIBUTORS.yml")
    dimensions = load_dimensions(cache_dir / "_data/quality_dimensions.yml")
    indicators = load_indicators(cache_dir / "_data/quality_indicators.yml")

    defaults, per_page = load_curated(data_dir / "curated_learn_more.yml")
    learn_more = merge_curated(collect_all(pages, source.base_url), defaults, per_page)

    fragments_dir = build_dir / "fragments"
    fragments_dir.mkdir(parents=True, exist_ok=True)

    page_entries = {}
    for page_id, record in sorted(pages.items()):
        cleaned = clean_body(record.body, source.base_url, tools)
        page_entries[page_id] = _page_entry(
            record, learn_more[page_id], source.base_url
        )
        header = FRAGMENT_HEADER.format(
            source=record.source_path,
            commit=pin.commit,
            url=f"{source.base_url}/{_page_slug(record)}",
            title=source.title,
            license=source.content_license,
            doi=source.doi,
        )
        (fragments_dir / f"{page_id}.md").write_text(header + cleaned, encoding="utf-8")

    content = {
        "upstream": {"repo": pin.repo, "commit": pin.commit, "ref": pin.ref},
        "pages": page_entries,
        "tools": {tool_id: asdict(tool) for tool_id, tool in sorted(tools.items())},
        "contributors": {
            name: asdict(person) for name, person in sorted(contributors.items())
        },
        "dimensions": {abbr: asdict(dim) for abbr, dim in sorted(dimensions.items())},
        "indicators": {abbr: asdict(ind) for abbr, ind in sorted(indicators.items())},
    }
    content_path = build_dir / "content.json"
    content_path.write_text(
        json.dumps(content, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return content_path


def main() -> None:
    pipeline_dir = Path(__file__).resolve().parents[2]
    path = assemble(pipeline_dir)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
