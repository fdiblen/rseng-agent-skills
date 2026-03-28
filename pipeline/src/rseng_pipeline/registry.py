"""Typed records for content-source registries.

These are the engine-level contracts; each content source ships its own
loader (see rseng_pipeline.sources) that parses upstream formats into them.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Tool:
    """One entry of the tool and resource registry."""

    id: str
    name: str
    description: str
    url: str
    catalog: str


@dataclass(frozen=True)
class Contributor:
    name: str
    git: str
    orcid: str | None = None
    email: str | None = None
    role: str | None = None
    affiliation: str | None = None


@dataclass(frozen=True)
class Dimension:
    """A software quality dimension from the rsqd JSON-LD registry."""

    abbreviation: str
    iri: str
    name: str
    description: str


@dataclass(frozen=True)
class Indicator:
    """A software quality indicator from the rsqi JSON-LD registry."""

    abbreviation: str
    iri: str
    name: str
    description: str
    keywords: tuple[str, ...]
    dimensions: tuple[str, ...]
    version: str
    status: str
    source_url: str
