"""Minimal HTTP helper shared by the online modules."""

from __future__ import annotations

import urllib.request


def http_get(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()
