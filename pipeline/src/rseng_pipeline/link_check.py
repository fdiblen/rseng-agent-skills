"""Check every external URL in generated artifacts.

Scans dist/ and each skill's generated references.md for http(s)
URLs, verifies each distinct URL once (quarantine list respected, HEAD
with GET fallback, parallel probes) and reports. Broken links fail the
run; quarantined links are skipped by design; network errors are warnings
so a flaky resolver cannot redden CI on its own.

Usage: python -m rseng_pipeline.link_check [root ...]
"""

from __future__ import annotations

import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .url_verify import URLCheck, load_quarantine, probe_url, verify_url

_URL_RE = re.compile(r"https?://[^\s)\"'<>{}\]`]+")
# A URL immediately followed by a placeholder opener is a documented
# template, not an address. _URL_RE stops at "<", so ".../works/doi:<DOI>"
# would be probed as ".../works/doi" and reported broken forever - a failure
# no content change could fix.
_PLACEHOLDER_NEXT = "<{"
# Catalogue snapshots are third-party data, truncated to 200 characters per
# entry. A URL inside them is neither ours to fix nor necessarily whole:
# truncation alone produced "http://op".
#
# Matched against the path RELATIVE to the scan root. Matching absolute parts
# meant a checkout under any directory called "data" - /home/me/data/repo, or
# a CI runner path - skipped every file and the check passed having read
# nothing. A link checker that silently verifies zero links is worse than none.
_SKIP_PARTS = ("data",)
_SCAN_SUFFIXES = {".md", ".mdc", ".toml", ".json", ".yml", ".yaml"}
_WORKERS = 16


def collect_urls(roots: list[Path]) -> dict[str, list[str]]:
    """Distinct URLs mapped to the files they appear in."""
    found: dict[str, list[str]] = {}
    for root in roots:
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix not in _SCAN_SUFFIXES:
                continue
            if any(part in _SKIP_PARTS for part in path.relative_to(root).parts):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for match in _URL_RE.finditer(text):
                nxt = text[match.end() : match.end() + 1]
                if nxt in _PLACEHOLDER_NEXT:
                    continue
                url = match.group().rstrip(".,;:")
                found.setdefault(url, []).append(str(path))
    return found


def check_urls(urls: list[str], quarantine: dict[str, str]) -> dict[str, URLCheck]:
    def check(url: str) -> URLCheck:
        return verify_url(url, quarantine=quarantine, probe=probe_url)

    with ThreadPoolExecutor(max_workers=_WORKERS) as pool:
        results = pool.map(check, urls)
    return dict(zip(urls, results, strict=True))


def main() -> None:
    pipeline_dir = Path(__file__).resolve().parents[2]
    repo_root = pipeline_dir.parent
    roots = (
        [Path(arg) for arg in sys.argv[1:]]
        if len(sys.argv) > 1
        else [repo_root / "dist", repo_root / "skills"]
    )
    roots = [root for root in roots if root.exists()]

    quarantine: dict[str, str] = {}
    for path in sorted(repo_root.glob("pipeline/data/url_quarantine.yml")):
        quarantine.update(load_quarantine(path))
    found = collect_urls(roots)
    print(f"checking {len(found)} distinct urls from {len(roots)} roots")
    results = check_urls(sorted(found), quarantine)

    broken = {u: c for u, c in results.items() if c.status == "broken"}
    errors = {u: c for u, c in results.items() if c.status == "error"}
    blocked = {u: c for u, c in results.items() if c.status == "blocked"}
    quarantined = [u for u, c in results.items() if c.status == "quarantined"]

    for url in quarantined:
        print(f"quarantined (skipped): {url}")
    for url, check in blocked.items():
        print(f"WARNING blocked {check.code}: {url}")
    for url, check in errors.items():
        print(f"WARNING unreachable: {url} ({check.reason[:80]})")
    for url, check in broken.items():
        files = ", ".join(sorted(set(found[url]))[:3])
        print(f"BROKEN {check.code}: {url} (in {files})")

    print(
        f"ok={sum(1 for c in results.values() if c.status == 'ok')} "
        f"broken={len(broken)} blocked={len(blocked)} errors={len(errors)} "
        f"quarantined={len(quarantined)}"
    )
    if broken:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
