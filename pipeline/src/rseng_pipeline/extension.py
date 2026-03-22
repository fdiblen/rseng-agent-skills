"""Locate content-source extensions.

A content source lives in extensions/<name>/ and provides the upstream
pin (upstream.lock), its per-file manifest, the page-to-skill taxonomy
and the source's data files (citation, quarantine, curated links). The
pipeline engine itself is source-agnostic; rsqkit is the bundled default
source.
"""

from __future__ import annotations

from pathlib import Path

DEFAULT_SOURCE = "rsqkit"


def extension_dir(repo_root: Path, name: str = DEFAULT_SOURCE) -> Path:
    ext = repo_root / "extensions" / name
    if not ext.is_dir():
        raise FileNotFoundError(f"no content-source extension at {ext}")
    return ext
