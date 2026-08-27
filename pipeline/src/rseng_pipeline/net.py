"""Minimal HTTP helper shared by the online modules."""

from __future__ import annotations

import urllib.parse
import urllib.request

# urlopen honours file:, ftp: and more. The URLs reaching this helper come
# from committed content and from catalog.yml, which is an open contribution
# surface - a proposal carrying file:///etc/passwd would otherwise be read
# and reported back. Only the two schemes this project actually fetches.
ALLOWED_SCHEMES = ("http", "https")


def http_get(url: str) -> bytes:
    scheme = urllib.parse.urlsplit(url).scheme.lower()
    if scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"refusing to fetch {scheme or 'scheme-less'} URL: {url}")
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()
