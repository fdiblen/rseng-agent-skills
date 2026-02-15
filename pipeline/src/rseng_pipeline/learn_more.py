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

from .cleaner import RSQKIT_BASE_URL, clean_body
from .parser import PageRecord, Section, build_section_tree, iter_sections
from .url_verify import ProbeFn, URLCheck, probe_url, verify_urls

_LINK_TARGET_RE = re.compile(r"\]\(\s*(https?://[^)\s]+)")
_REF_DEF_TARGET_RE = re.compile(r"^\[[^\]]+\]:\s*(https?://\S+)", re.MULTILINE)


@dataclass(frozen=True)
class LearnMore:
    """Learn-more pointers for one page."""

    page_id: str
    rsqkit_url: str
    external: tuple[str, ...]
    training: tuple[str, ...]


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


def collect_learn_more(record: PageRecord) -> LearnMore:
    """Extract learn-more pointers from one page record."""
    cleaned = clean_body(record.body)
    sections = build_section_tree(cleaned)

    training_links: list[str] = []
    for training in _training_sections(sections):
        training_links.extend(_links_in(training.content))
        for child in iter_sections(training.children):
            training_links.extend(_links_in(child.content))

    external = [
        url for url in _links_in(cleaned) if not url.startswith(RSQKIT_BASE_URL)
    ]
    return LearnMore(
        page_id=record.page_id,
        rsqkit_url=f"{RSQKIT_BASE_URL}/{record.page_id}",
        external=_dedupe(external),
        training=_dedupe(training_links),
    )


def collect_all(pages: dict[str, PageRecord]) -> dict[str, LearnMore]:
    return {page_id: collect_learn_more(rec) for page_id, rec in pages.items()}


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
        url for entry in entries.values() for url in (*entry.external, *entry.training)
    }
    checks = verify_urls(sorted(all_urls), quarantine=quarantine, probe=probe)

    def keep(urls: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(url for url in urls if checks[url].status == "ok")

    filtered = {
        page_id: replace(
            entry, external=keep(entry.external), training=keep(entry.training)
        )
        for page_id, entry in entries.items()
    }
    return filtered, checks
