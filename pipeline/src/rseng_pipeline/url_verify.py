"""Verify external URLs before they are propagated into generated content.

A quarantine list (data/url_quarantine.yml) holds URLs a human has flagged;
those are rejected without probing. Everything else gets an HTTP HEAD probe
with a GET fallback for servers that refuse HEAD. The probe function is
injectable so callers and tests can run without network access.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_TIMEOUT = 15
USER_AGENT = "rseng-agent-skills-pipeline"

# HEAD is often rejected by CDNs; these statuses trigger one GET retry.
_RETRY_WITH_GET = {403, 405, 501}

ProbeFn = Callable[[str], int]


@dataclass(frozen=True)
class URLCheck:
    url: str
    status: str  # "ok" | "quarantined" | "broken" | "error"
    code: int | None = None
    reason: str = ""


def load_quarantine(path: Path) -> dict[str, str]:
    """Quarantined URLs mapped to the reason they are blocked."""
    entries = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    return {entry["url"]: entry.get("reason", "flagged") for entry in entries}


def _request(url: str, method: str, timeout: int) -> int:
    request = urllib.request.Request(
        url, method=method, headers={"User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status


def probe_url(url: str, timeout: int = DEFAULT_TIMEOUT) -> int:
    """Return the HTTP status for a URL, preferring HEAD over GET."""
    try:
        return _request(url, "HEAD", timeout)
    except urllib.error.HTTPError as error:
        if error.code in _RETRY_WITH_GET:
            try:
                return _request(url, "GET", timeout)
            except urllib.error.HTTPError as get_error:
                return get_error.code
        return error.code


def verify_url(
    url: str,
    quarantine: dict[str, str] | None = None,
    probe: ProbeFn = probe_url,
) -> URLCheck:
    quarantine = quarantine or {}
    if url in quarantine:
        return URLCheck(url=url, status="quarantined", reason=quarantine[url])
    try:
        code = probe(url)
    except Exception as error:  # DNS failure, timeout, TLS error, ...
        return URLCheck(url=url, status="error", reason=str(error))
    status = "ok" if code < 400 else "broken"
    return URLCheck(url=url, status=status, code=code)


def verify_urls(
    urls: Iterable[str],
    quarantine: dict[str, str] | None = None,
    probe: ProbeFn = probe_url,
) -> dict[str, URLCheck]:
    """Verify each distinct URL once; results keyed by URL."""
    results: dict[str, URLCheck] = {}
    for url in urls:
        if url not in results:
            results[url] = verify_url(url, quarantine=quarantine, probe=probe)
    return results
