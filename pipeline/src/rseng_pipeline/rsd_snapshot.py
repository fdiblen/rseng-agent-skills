"""Snapshot software catalogs from Research Software Directory instances.

Writes compact, committed JSON files (one per instance) into the
rseng-software-reuse skill folder so agents can suggest existing research
software directly, without a live query. Entries carry keywords and
programming languages so suggestions can match on domain and stack, not
just free text. Refreshed explicitly (or by the sync workflow), never
during normal builds.

Usage: python -m rseng_pipeline.rsd_snapshot
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path

from .net import http_get as _get

INSTANCES = [
    {
        "name": "escience",
        "title": "Netherlands eScience Center RSD",
        "base": "https://research-software-directory.org",
    },
    {
        "name": "helmholtz",
        "title": "Helmholtz RSD",
        "base": "https://helmholtz.software",
    },
]

PAGE = 500
SUMMARY_MAX = 200
LANGUAGES_MAX = 3
SELECT = "slug,brand_name,short_statement,keyword(value),repository_url(languages)"


def fetch_instance(base: str) -> list[dict]:
    entries: list[dict] = []
    offset = 0
    while True:
        url = (
            f"{base}/api/v1/software"
            f"?select={SELECT}&order=slug&limit={PAGE}&offset={offset}"
        )
        page = json.loads(_get(url))
        entries.extend(page)
        if len(page) < PAGE:
            return entries
        offset += PAGE


def _languages(repository_url: object) -> list[str]:
    """Top languages by code volume; the embed is an object on some
    instances and a single-element array on others."""
    if isinstance(repository_url, list):
        repository_url = repository_url[0] if repository_url else None
    if not isinstance(repository_url, dict):
        return []
    counts = repository_url.get("languages")
    if not isinstance(counts, dict):
        return []
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return [name for name, _ in ranked[:LANGUAGES_MAX]]


def build_entry(row: dict) -> dict:
    summary = " ".join(str(row.get("short_statement") or "").split())
    entry = {
        "name": row.get("brand_name") or row["slug"],
        "slug": row["slug"],
        "summary": summary[:SUMMARY_MAX],
    }
    keywords = sorted({k["value"] for k in row.get("keyword") or [] if k.get("value")})
    if keywords:
        entry["keywords"] = keywords
    languages = _languages(row.get("repository_url"))
    if languages:
        entry["languages"] = languages
    return entry


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    data_dir = repo_root / "skills" / "rseng-software-reuse" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.datetime.now(tz=datetime.UTC).date().isoformat()
    for instance in INSTANCES:
        rows = fetch_instance(instance["base"])
        snapshot = {
            "snapshot_date": today,
            "instance": {
                "name": instance["name"],
                "title": instance["title"],
                "base": instance["base"],
                "software_url": instance["base"] + "/software/<slug>",
                "count": len(rows),
            },
            "software": [build_entry(row) for row in rows],
        }
        out = data_dir / f"rsd-{instance['name']}.json"
        out.write_text(
            json.dumps(snapshot, indent=0, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {out.relative_to(repo_root)} ({len(rows)} entries)")


if __name__ == "__main__":
    main()
