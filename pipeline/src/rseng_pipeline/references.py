"""Generate each skill's references.md from the build artifacts.

Every skill gets ONE simple generated file, references.md, with a
section per installed content source: the source's citation line, links
to the source pages the skill draws on, and verified "Learn more"
pointers. No page fragments, tool lists or indicator checklists are
written; agents follow the links for full source material.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml

GENERATED_HEADER = (
    "<!-- Generated file - do not edit. Rebuilt by the rseng-agent-skills\n"
    "     pipeline from the configured content sources; see extensions/. -->\n\n"
)


def load_taxonomy(path: Path) -> dict[str, dict]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))["skills"]


def skill_page_ids(entry: dict) -> list[str]:
    return (
        list(entry.get("pages") or [])
        + list(entry.get("concept_pages") or [])
        + list(entry.get("role_pages") or [])
    )


def _source_section(
    source_title: str,
    citation: str,
    page_ids: list[str],
    content: dict,
) -> str:
    missing = [pid for pid in page_ids if pid not in content["pages"]]
    if missing:
        raise KeyError(f"pages missing from content build: {missing}")
    pages = [content["pages"][pid] for pid in page_ids]

    lines = [f"## {source_title}", "", citation, ""]
    if pages:
        lines.append("Source pages:")
        lines.append("")
        lines.extend(f"- {page['title']}: {page['rsqkit_url']}" for page in pages)
        lines.append("")

    seen: set[str] = set()
    learn: list[str] = []
    for page in pages:
        for curated in page["learn_more"]["curated"]:
            if curated["url"] not in seen:
                seen.add(curated["url"])
                learn.append(f"- [{curated['label']}]({curated['url']})")
    for page in pages:
        for url in page["learn_more"]["training"] + page["learn_more"]["external"]:
            if url not in seen:
                seen.add(url)
                learn.append(f"- {url}")
    if learn:
        lines.append("Learn more:")
        lines.append("")
        lines.extend(learn)
        lines.append("")
    return "\n".join(lines)


INDEPENDENT_HEADER = (
    "<!-- Generated file - do not edit. Derived by the rseng-agent-skills\n"
    "     pipeline from this skill's own curated links in SKILL.md. -->\n\n"
)


def extract_curated(skill_md: str) -> tuple[str, list[str]]:
    """Pull the trailing citation paragraph and Learn-more bullets out
    of a source-independent skill's SKILL.md."""
    lines = skill_md.splitlines()
    bullets: list[str] = []
    collecting = False
    for line in lines:
        if "Learn more (verified):" in line:
            collecting = True
            continue
        if collecting:
            if line.startswith("  - "):
                bullets.append(line[4:].strip())
            elif line.startswith("    ") and bullets:
                bullets[-1] += " " + line.strip()
            elif line.strip() == "":
                continue
            else:
                collecting = False
    citation = ""
    if "\n---\n" in skill_md:
        tail = skill_md.rsplit("\n---\n", 1)[1].strip()
        if tail and not tail.startswith("#"):
            citation = " ".join(tail.split())
    return citation, bullets


def independent_reference(skill_md: str) -> str:
    citation, bullets = extract_curated(skill_md)
    lines = [INDEPENDENT_HEADER + "# References", ""]
    if citation:
        lines += [citation, ""]
    if bullets:
        lines += ["Learn more:", ""]
        lines += [f"- {b}" for b in bullets]
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def generate_references(
    skills_dir: Path,
    sources: list[tuple[object, Path, dict]],
) -> list[Path]:
    """Write references.md for every skill.

    ``sources`` is a list of (source_config, taxonomy_path, content)
    tuples, one per installed extension, in order.
    """
    per_skill: dict[str, list[str]] = {}
    for source, taxonomy_path, content in sources:
        citation = yaml.safe_load(
            (source.dir / "data" / "citation.yml").read_text(encoding="utf-8")
        )
        citation_md = " ".join(str(citation.get("markdown", "")).split())
        taxonomy = load_taxonomy(taxonomy_path)
        for skill_name, entry in taxonomy.items():
            section = _source_section(
                source.title, citation_md, skill_page_ids(entry), content
            )
            per_skill.setdefault(skill_name, []).append(section)

    written = []
    for skill_name, sections in sorted(per_skill.items()):
        skill_dir = skills_dir / skill_name
        # The old per-source folder layout is fully superseded.
        shutil.rmtree(skill_dir / "references", ignore_errors=True)
        out = skill_dir / "references.md"
        body = GENERATED_HEADER + "# References\n\n" + "\n".join(sections)
        out.write_text(body.rstrip() + "\n", encoding="utf-8")
        written.append(out)

    # Source-independent skills: derive references.md from the curated
    # links already maintained in their SKILL.md, so every skill ships
    # exactly one references file with no duplicated upkeep.
    for skill_dir in sorted(skills_dir.iterdir()):
        skill_md_path = skill_dir / "SKILL.md"
        if not skill_md_path.is_file() or skill_dir.name in per_skill:
            continue
        out = skill_dir / "references.md"
        out.write_text(
            independent_reference(skill_md_path.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
        written.append(out)
    return written


def main() -> None:
    from .extension import extension_dir, list_extensions
    from .source import load_source

    pipeline_dir = Path(__file__).resolve().parents[2]
    repo_root = pipeline_dir.parent
    sources = []
    for name in list_extensions(repo_root):
        content = json.loads(
            (pipeline_dir / "build" / name / "content.json").read_text(encoding="utf-8")
        )
        sources.append(
            (
                load_source(repo_root, name),
                extension_dir(repo_root, name) / "taxonomy.yml",
                content,
            )
        )
    written = generate_references(repo_root / "skills", sources)
    print(f"wrote references.md for {len(written)} skills")


if __name__ == "__main__":
    main()
