"""Fetch pinned RSQKit sources into a local cache.

The upstream pin (repository, commit, source paths) lives in upstream.lock.
Files are downloaded from raw.githubusercontent.com at the pinned commit and
recorded in a manifest with SHA-256 hashes, so later runs can verify cache
integrity instead of re-downloading.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import tomllib

RAW_BASE = "https://raw.githubusercontent.com"
TREE_API = "https://api.github.com/repos/{repo}/git/trees/{commit}?recursive=1"
MANIFEST_NAME = "manifest.json"

_ALLOWED_SUFFIXES = (".md", ".yml", ".yaml")


@dataclass(frozen=True)
class UpstreamPin:
    """Pinned upstream repository and the source files taken from it."""

    repo: str
    ref: str
    commit: str
    paths: tuple[str, ...]
    data_globs: tuple[str, ...]


def load_pin(lock_path: Path) -> UpstreamPin:
    data = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    upstream = data["upstream"]
    sources = data["sources"]
    repo = upstream["repo"].removeprefix("https://github.com/").strip("/")
    return UpstreamPin(
        repo=repo,
        ref=upstream["ref"],
        commit=upstream["commit"],
        paths=tuple(sources["paths"]),
        data_globs=tuple(sources["data_globs"]),
    )


def _glob_match(path: str, pattern: str) -> bool:
    """Glob match where ``*`` does not cross directory boundaries."""
    path_parts = path.split("/")
    pattern_parts = pattern.split("/")
    if len(path_parts) != len(pattern_parts):
        return False
    return all(
        fnmatch.fnmatch(part, pat)
        for part, pat in zip(path_parts, pattern_parts, strict=True)
    )


def selects(pin: UpstreamPin, path: str) -> bool:
    """Whether the pin's source lists select the given repository path.

    Template pages and non-markdown/YAML files are never selected.
    """
    name = path.rsplit("/", 1)[-1]
    if name.startswith("TEMPLATE_"):
        return False
    if not path.endswith(_ALLOWED_SUFFIXES):
        return False
    if any(path.startswith(prefix) for prefix in pin.paths):
        return True
    return any(_glob_match(path, pattern) for pattern in pin.data_globs)


def _get(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def list_upstream_files(pin: UpstreamPin) -> list[str]:
    """Enumerate selected files from the pinned commit's git tree."""
    tree = json.loads(_get(TREE_API.format(repo=pin.repo, commit=pin.commit)))
    return sorted(
        entry["path"]
        for entry in tree["tree"]
        if entry["type"] == "blob" and selects(pin, entry["path"])
    )


def load_manifest(cache_dir: Path) -> dict | None:
    manifest_path = cache_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        return None
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def verify_cache(cache_dir: Path) -> list[str]:
    """Return problems found in the cache; an empty list means it is intact."""
    manifest = load_manifest(cache_dir)
    if manifest is None:
        return [f"missing {MANIFEST_NAME}"]
    problems = []
    for path, expected in manifest["files"].items():
        cached = cache_dir / path
        if not cached.is_file():
            problems.append(f"missing file: {path}")
        elif _sha256(cached.read_bytes()) != expected:
            problems.append(f"hash mismatch: {path}")
    return problems


def fetch(
    pin: UpstreamPin,
    cache_dir: Path,
    files: list[str] | None = None,
    force: bool = False,
) -> dict[str, str]:
    """Download selected files into the cache and return their SHA-256 map.

    Files already cached with a matching hash for the pinned commit are kept
    as they are; pass ``force=True`` to re-download everything.
    """
    if files is None:
        files = list_upstream_files(pin)
    previous: dict[str, str] = {}
    manifest = load_manifest(cache_dir)
    if not force and manifest and manifest.get("commit") == pin.commit:
        previous = manifest.get("files", {})

    hashes: dict[str, str] = {}
    for path in files:
        target = cache_dir / path
        if path in previous and target.is_file():
            cached_hash = _sha256(target.read_bytes())
            if cached_hash == previous[path]:
                hashes[path] = cached_hash
                continue
        data = _get(f"{RAW_BASE}/{pin.repo}/{pin.commit}/{path}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        hashes[path] = _sha256(data)

    cache_dir.mkdir(parents=True, exist_ok=True)
    manifest_body = {"repo": pin.repo, "commit": pin.commit, "files": hashes}
    (cache_dir / MANIFEST_NAME).write_text(
        json.dumps(manifest_body, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return hashes


def main() -> None:
    from .extension import extension_dir, list_extensions

    pipeline_dir = Path(__file__).resolve().parents[2]
    repo_root = pipeline_dir.parent
    for name in list_extensions(repo_root):
        pin = load_pin(extension_dir(repo_root, name) / "upstream.lock")
        hashes = fetch(pin, pipeline_dir / "cache" / name)
        print(f"{name}: fetched {len(hashes)} files at {pin.commit[:8]}")


if __name__ == "__main__":
    main()
