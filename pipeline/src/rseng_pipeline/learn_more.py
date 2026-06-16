"""Collect per-page "Learn more" pointers.

Every page contributes its own RSQKit deep link plus the external references
found in its body; links inside Training sections are tracked separately so
skills can present curated training material distinctly. Tool tags are left
out on purpose - tool homepages already reach skills through the tool
registry. Verification runs through url_verify with an injectable probe.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from pathlib import Path

import yaml

from .cleaner import clean_body
from .parser import PageRecord, Section, build_section_tree, iter_sections
from .url_verify import ProbeFn, URLCheck, probe_url, verify_urls

_LINK_TARGET_RE = re.compile(r"\]\(\s*(https?://[^)\s]+)")
_REF_DEF_TARGET_RE = re.compile(r"^\[[^\]]+\]:\s*(https?://\S+)", re.MULTILINE)


@dataclass(frozen=True)
class CuratedSource:
    label: str
    url: str


@dataclass(frozen=True)
class LearnMore:
    """Learn-more pointers for one page."""

    page_id: str
    page_url: str
    external: tuple[str, ...]
    training: tuple[str, ...]
    curated: tuple[CuratedSource, ...] = ()


def _links_in(text: str) -> list[str]:
    return _LINK_TARGET_RE.findall(text) + _REF_DEF_TARGET_RE.findall(text)


def _training_sections(sections: list[Section]) -> list[Section]:
    return [
        section
        for section in iter_sections(sections)
        if section.title.strip().lower() == "training"
    ]


def _dedupe(urls: list[str]) -> tuple[str, ...]:
    seen = set()
    result = []
    for url in urls:
        trimmed = url.rstrip(").,")
        if trimmed not in seen:
            seen.add(trimmed)
            result.append(trimmed)
    return tuple(result)


def collect_learn_more(
    record: PageRecord, base_url: str, slug_style: str = "stem"
) -> LearnMore:
    """Extract learn-more pointers from one page record."""
    cleaned = clean_body(record.body, base_url)
    sections = build_section_tree(cleaned)

    training_links: list[str] = []
    for training in _training_sections(sections):
        training_links.extend(_links_in(training.content))
        for child in iter_sections(training.children):
            training_links.extend(_links_in(child.content))

    external = [url for url in _links_in(cleaned) if not url.startswith(base_url)]
    path = Path(record.source_path)
    slug = str(path.with_suffix("")) if slug_style == "path" else path.stem
    return LearnMore(
        page_id=record.page_id,
        page_url=f"{base_url}/{slug}",
        external=_dedupe(external),
        training=_dedupe(training_links),
    )


def collect_all(
    pages: dict[str, PageRecord], base_url: str, slug_style: str = "stem"
) -> dict[str, LearnMore]:
    return {
        page_id: collect_learn_more(rec, base_url, slug_style)
        for page_id, rec in pages.items()
    }


def load_curated(
    path: Path,
) -> tuple[tuple[CuratedSource, ...], dict[str, tuple[CuratedSource, ...]]]:
    """Curated sources: pack-wide defaults plus per-page additions."""
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def sources(items) -> tuple[CuratedSource, ...]:
        return tuple(
            CuratedSource(label=item["label"], url=item["url"]) for item in items or ()
        )

    per_page = {
        page_id: sources(items) for page_id, items in (data.get("pages") or {}).items()
    }
    return sources(data.get("defaults")), per_page


def merge_curated(
    entries: dict[str, LearnMore],
    defaults: tuple[CuratedSource, ...],
    per_page: dict[str, tuple[CuratedSource, ...]],
) -> dict[str, LearnMore]:
    """Attach curated sources to every page's learn-more entry."""
    merged = {}
    for page_id, entry in entries.items():
        curated = per_page.get(page_id, ()) + defaults
        merged[page_id] = replace(entry, curated=curated)
    return merged


def verify_learn_more(
    entries: dict[str, LearnMore],
    quarantine: dict[str, str] | None = None,
    probe: ProbeFn = probe_url,
) -> tuple[dict[str, LearnMore], dict[str, URLCheck]]:
    """Verify every distinct URL once and drop the ones that fail.

    Returns the filtered entries plus the full check results so callers can
    report or persist what was rejected.
    """
    all_urls = {
        url
        for entry in entries.values()
        for url in (
            *entry.external,
            *entry.training,
            *(source.url for source in entry.curated),
        )
    }
    checks = verify_urls(sorted(all_urls), quarantine=quarantine, probe=probe)

    def keep(urls: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(url for url in urls if checks[url].status == "ok")

    filtered = {
        page_id: replace(
            entry,
            external=keep(entry.external),
            training=keep(entry.training),
            curated=tuple(
                source for source in entry.curated if checks[source.url].status == "ok"
            ),
        )
        for page_id, entry in entries.items()
    }
    return filtered, checks
