"""Committed per-file manifest of the pinned upstream sources.

extensions/<source>/upstream.manifest.json records the SHA-256 of every source file
at the pinned commit. The sync classifier diffs live upstream content
against it to detect and classify changes without trusting timestamps.

Usage: python -m rseng_pipeline.lock_manifest   (refresh from the cache)
"""

from __future__ import annotations

import json
from pathlib import Path

from .fetcher import load_manifest, load_pin, verify_cache

MANIFEST_FILE = "upstream.manifest.json"


def write_lock_manifest(pipeline_dir: Path, ext_dir: Path) -> Path:
    """Copy the verified cache manifest into the committed lock manifest."""
    cache_dir = pipeline_dir / "cache" / ext_dir.name
    problems = verify_cache(cache_dir)
    if problems:
        raise RuntimeError(f"cache not usable: {problems}")
    cache_manifest = load_manifest(cache_dir)
    assert cache_manifest is not None
    pin = load_pin(ext_dir / "upstream.lock")
    if cache_manifest["commit"] != pin.commit:
        raise RuntimeError(
            f"cache is at {cache_manifest['commit'][:8]}, lock pins "
            f"{pin.commit[:8]}; refetch first"
        )
    out = ext_dir / MANIFEST_FILE
    out.write_text(
        json.dumps(cache_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out


def read_lock_manifest(ext_dir: Path) -> dict:
    return json.loads((ext_dir / MANIFEST_FILE).read_text(encoding="utf-8"))


def main() -> None:
    from .extension import extension_dir, list_extensions

    pipeline_dir = Path(__file__).resolve().parents[2]
    for name in list_extensions(pipeline_dir.parent):
        ext = extension_dir(pipeline_dir.parent, name)
        path = write_lock_manifest(pipeline_dir, ext)
        files = len(read_lock_manifest(ext)["files"])
        print(f"{name}: wrote {path.name} with {files} file hashes")


if __name__ == "__main__":
    main()
