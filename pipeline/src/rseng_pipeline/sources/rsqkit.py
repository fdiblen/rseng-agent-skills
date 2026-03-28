"""RSQKit source plugin: registry loaders.

Parses the RSQKit `_data/*.yml` registry files (plain YAML for tools and
contributors, EVERSE rsqd/rsqi JSON-LD for dimensions and indicators)
into the engine's typed records.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from ..registry import Contributor, Dimension, Indicator, Tool


def _squash(text: str) -> str:
    """Collapse folded-scalar line breaks and stray whitespace."""
    return " ".join(str(text).split())


def load_tools(path: Path) -> dict[str, Tool]:
    """Tool registry keyed by tool id."""
    entries = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    tools: dict[str, Tool] = {}
    for entry in entries:
        tool = Tool(
            id=entry["id"],
            name=entry.get("name") or entry["id"],
            description=_squash(entry.get("description", "")),
            url=entry.get("url", ""),
            catalog=entry.get("catalog", ""),
        )
        tools[tool.id] = tool
    return tools


def load_contributors(path: Path) -> dict[str, Contributor]:
    """Contributor registry keyed by full name."""
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    contributors: dict[str, Contributor] = {}
    for name, info in data.items():
        if not isinstance(info, dict):
            continue
        contributors[name] = Contributor(
            name=name,
            git=str(info.get("git", "")),
            orcid=info.get("orcid"),
            email=info.get("email"),
            role=info.get("role"),
            affiliation=info.get("affiliation"),
        )
    return contributors


def _iri_tail(iri: str) -> str:
    # Upstream IRIs occasionally carry stray whitespace; strip it, but keep
    # genuine content errors (e.g. misspelled dimension ids) untouched so
    # they stay visible to validation.
    return iri.strip().rstrip("/").rsplit("/", 1)[-1].strip()


def _refs(value) -> tuple[str, ...]:
    """Abbreviations from a JSON-LD reference (single or list of @id dicts)."""
    if not value:
        return ()
    if isinstance(value, dict):
        value = [value]
    return tuple(_iri_tail(ref["@id"]) for ref in value if isinstance(ref, dict))


def load_dimensions(path: Path) -> dict[str, Dimension]:
    """Quality dimensions keyed by abbreviation."""
    entries = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    dimensions: dict[str, Dimension] = {}
    for entry in entries:
        dim = Dimension(
            abbreviation=entry["abbreviation"],
            iri=entry.get("@id", ""),
            name=entry.get("name", entry["abbreviation"]),
            description=_squash(entry.get("description", "")),
        )
        dimensions[dim.abbreviation] = dim
    return dimensions


def load_indicators(path: Path) -> dict[str, Indicator]:
    """Quality indicators keyed by abbreviation."""
    entries = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    indicators: dict[str, Indicator] = {}
    for entry in entries:
        source = entry.get("source") or {}
        if isinstance(source, list):
            source = source[0] if source else {}
        indicator = Indicator(
            abbreviation=entry["abbreviation"],
            iri=entry.get("@id", ""),
            name=_squash(entry.get("name", entry["abbreviation"])),
            description=_squash(entry.get("description", "")),
            keywords=tuple(entry.get("keywords") or ()),
            dimensions=_refs(entry.get("qualityDimension")),
            version=str(entry.get("version", "")),
            status=str(entry.get("status", "")),
            source_url=source.get("url", "") if isinstance(source, dict) else "",
        )
        indicators[indicator.abbreviation] = indicator
    return indicators
