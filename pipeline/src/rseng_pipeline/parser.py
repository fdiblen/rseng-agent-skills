"""Parse RSQKit markdown pages into normalized page records.

Upstream frontmatter is not fully uniform: hub pages use ``indicators``
instead of ``quality_indicators``, a handful of pages have no ``page_id``,
and ``related_pages`` is a mapping of page groups to id lists. The record
returned here smooths those differences out so downstream stages never deal
with raw frontmatter.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import frontmatter

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_FENCE_RE = re.compile(r"^(```|~~~)")
_TOOL_TAG_RE = re.compile(r"\{%-?\s*tool\s+\"([^\"]+)\"\s*-?%\}")

_NORMALIZED_KEYS = {
    "page_id",
    "title",
    "description",
    "keywords",
    "contributors",
    "related_pages",
    "quality_indicators",
    "indicators",
    "child_pages",
}


@dataclass
class PageRecord:
    """One RSQKit page, normalized."""

    page_id: str
    title: str
    description: str
    keywords: list[str]
    contributors: list[str]
    related_pages: dict[str, list[str]]
    quality_indicators: list[str]
    child_pages: list[str]
    body: str
    source_path: str
    extra: dict = field(default_factory=dict)


def _as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value]


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def parse_page(text: str, source_path: str) -> PageRecord:
    post = frontmatter.loads(text)
    meta = dict(post.metadata)

    related = meta.get("related_pages") or {}
    if isinstance(related, list):
        related = {"tasks": related}
    related = {str(group): _as_list(ids) for group, ids in related.items()}

    indicators = _dedupe(
        _as_list(meta.get("quality_indicators")) + _as_list(meta.get("indicators"))
    )

    return PageRecord(
        page_id=str(meta.get("page_id") or Path(source_path).stem),
        title=str(meta.get("title", "")),
        description=str(meta.get("description", "")),
        keywords=_as_list(meta.get("keywords")),
        contributors=_as_list(meta.get("contributors")),
        related_pages=related,
        quality_indicators=indicators,
        child_pages=_as_list(meta.get("child_pages")),
        body=post.content,
        source_path=source_path,
        extra={k: v for k, v in meta.items() if k not in _NORMALIZED_KEYS},
    )


def parse_page_file(path: Path, root: Path | None = None) -> PageRecord:
    source = path.relative_to(root) if root else path
    return parse_page(path.read_text(encoding="utf-8"), str(source))


def load_pages(cache_dir: Path) -> dict[str, PageRecord]:
    """Parse every cached page, keyed by page_id."""
    records: dict[str, PageRecord] = {}
    for md_file in sorted(cache_dir.glob("pages/**/*.md")):
        record = parse_page_file(md_file, cache_dir)
        records[record.page_id] = record
    return records


@dataclass
class Section:
    """A heading with its direct text and nested subsections."""

    level: int
    title: str
    content: str
    children: list[Section] = field(default_factory=list)


def build_section_tree(body: str) -> list[Section]:
    """Build a nested section tree from ATX headings.

    Headings inside fenced code blocks are ignored. Text before the first
    heading is not part of any section; take it from the body directly.
    """
    root = Section(level=0, title="", content="")
    stack = [root]
    content_lines: dict[int, list[str]] = {id(root): []}
    in_fence = False

    for line in body.splitlines():
        if _FENCE_RE.match(line.strip()):
            in_fence = not in_fence
        heading = None if in_fence else _HEADING_RE.match(line)
        if heading is None:
            content_lines[id(stack[-1])].append(line)
            continue
        section = Section(
            level=len(heading.group(1)), title=heading.group(2), content=""
        )
        while stack[-1].level >= section.level:
            stack.pop()
        stack[-1].children.append(section)
        stack.append(section)
        content_lines[id(section)] = []

    def finalize(section: Section) -> None:
        section.content = "\n".join(content_lines[id(section)]).strip("\n")
        for child in section.children:
            finalize(child)

    finalize(root)
    return root.children


def iter_sections(sections: list[Section]):
    """Yield every section in the tree, depth first."""
    for section in sections:
        yield section
        yield from iter_sections(section.children)


def extract_tool_refs(body: str) -> list[str]:
    """Tool registry ids referenced via ``{% tool "..." %}`` tags, in order."""
    return _dedupe(_TOOL_TAG_RE.findall(body))
