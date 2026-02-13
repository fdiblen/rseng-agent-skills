"""Load RSQKit registry data files into normalized lookups."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


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
