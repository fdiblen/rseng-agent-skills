"""Content-source configuration.

Each extension provides a source.yml describing the upstream content it
contributes: its human title, site and base URL for resolved links, DOI
and content license for attribution. The engine reads everything
source-specific from here rather than hardcoding any single source.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .extension import DEFAULT_SOURCE, extension_dir


@dataclass(frozen=True)
class SourceConfig:
    name: str
    title: str
    site: str
    base_url: str
    doi: str
    content_license: str
    dir: Path
    # How page URLs derive from source paths: "stem" (filename only,
    # e.g. Jekyll permalinks) or "path" (relative path without suffix,
    # e.g. docsify routes with subdirectories).
    slug_style: str = "stem"


def load_source(repo_root: Path, name: str = DEFAULT_SOURCE) -> SourceConfig:
    ext = extension_dir(repo_root, name)
    data = yaml.safe_load((ext / "source.yml").read_text(encoding="utf-8"))
    return SourceConfig(
        name=data["name"],
        title=" ".join(str(data["title"]).split()),
        site=data["site"],
        base_url=data["base_url"].rstrip("/"),
        doi=str(data["doi"]),
        content_license=data["content_license"],
        dir=ext,
        slug_style=data.get("slug_style", "stem"),
    )
