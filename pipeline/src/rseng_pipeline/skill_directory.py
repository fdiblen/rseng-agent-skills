"""Generate the grouped skill directory in AGENTS.md and the router.

One source of truth for "which skill covers what": the cluster map
below plus each skill's frontmatter brief. Rewrites the blocks between
the skill-directory markers in AGENTS.md and in
skills/rseng-quality-framework/SKILL.md, so the two lists can never
drift apart. Fails loudly when a skill is missing from the map.

Usage: python -m rseng_pipeline.skill_directory
"""

from __future__ import annotations

from pathlib import Path

import frontmatter

from .adapters import _brief

START = "<!-- skill-directory:start (generated - do not edit by hand) -->"
END = "<!-- skill-directory:end -->"

# Primary phase per cluster: when in a task each practice area is
# considered first (revisited whenever relevant).
PHASES: dict[str, list[str]] = {
    "Start": [
        "Planning and operations",
        "Research data",
        "Publishing, credit and reuse",
        "Specialized",
    ],
    "During": [
        "Core engineering",
        "Reproducibility and workflows",
        "Numerics and performance",
    ],
    "Finish": [
        "Integrity, security and compliance",
        "Communication and interfaces",
        "Community and people",
    ],
}

CLUSTERS: dict[str, list[str]] = {
    "Core engineering": [
        "rseng-testing",
        "rseng-ci-cd",
        "rseng-code-quality",
        "rseng-software-design",
        "rseng-defensive-coding",
        "rseng-debugging",
        "rseng-version-control-review",
        "rseng-software-metrics",
        "rseng-pair-programming",
        "rseng-code-review",
        "rseng-project-scaffolding",
    ],
    "Reproducibility and workflows": [
        "rseng-reproducible-environments",
        "rseng-reproducibility",
        "rseng-workflows",
        "rseng-provenance",
        "rseng-notebooks",
    ],
    "Research data": [
        "rseng-data-management",
        "rseng-scientific-file-formats",
        "rseng-big-data-processing",
        "rseng-data-management-plans",
    ],
    "Numerics and performance": [
        "rseng-numerical-accuracy",
        "rseng-performance-profiling",
        "rseng-gpu-computing",
        "rseng-hpc-computing",
    ],
    "Publishing, credit and reuse": [
        "rseng-publishing-releasing",
        "rseng-software-publishing",
        "rseng-archiving",
        "rseng-citation-metadata",
        "rseng-citation-hygiene",
        "rseng-licensing",
        "rseng-license-compliance",
        "rseng-fair-software",
        "rseng-fair-ml",
        "rseng-fairguard",
        "rseng-software-reuse",
        "rseng-discovery",
        "rseng-dependency-management",
        "rseng-software-peer-review",
        "rseng-open-science-practices",
    ],
    "Integrity, security and compliance": [
        "rseng-security",
        "rseng-agent-security",
        "rseng-regulatory-compliance",
        "rseng-research-integrity",
        "rseng-fact-checking",
        "rseng-honesty",
        "rseng-human-verification",
        "rseng-ai-declaration",
    ],
    "Community and people": [
        "rseng-community-governance",
        "rseng-community-metrics",
        "rseng-contributor-onboarding",
        "rseng-user-support",
        "rseng-trainer",
    ],
    "Communication and interfaces": [
        "rseng-documentation",
        "rseng-science-communication",
        "rseng-storytelling",
        "rseng-ux-accessibility",
    ],
    "Planning and operations": [
        "rseng-management-planning",
        "rseng-project-kickoff",
        "rseng-project-tracking",
        "rseng-lessons-learned",
        "rseng-maintenance-sustainability",
        "rseng-green-computing",
    ],
    "Specialized": [
        "rseng-language-guides",
        "rseng-legacy-code",
        "rseng-open-source-migration",
        "rseng-scientific-visualization",
    ],
}


def load_briefs(skills_dir: Path) -> dict[str, str]:
    briefs = {}
    for skill_dir in sorted(skills_dir.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        post = frontmatter.loads(skill_md.read_text(encoding="utf-8"))
        brief = _brief(str(post.get("description", "")))
        for prefix in ("Covers ", "Explains "):
            brief = brief.removeprefix(prefix)
        briefs[skill_dir.name] = brief
    return briefs


def directory_block(skills_dir: Path, include_router: bool) -> str:
    briefs = load_briefs(skills_dir)
    mapped = {name for names in CLUSTERS.values() for name in names}
    known = set(briefs) - {"rseng-quality-framework"}
    missing = known - mapped
    stale = mapped - set(briefs)
    if missing or stale:
        raise SystemExit(
            f"skill_directory cluster map out of date - missing: {sorted(missing)}; "
            f"stale: {sorted(stale)}"
        )
    lines = []
    if include_router:
        lines += [
            '- Unsure where to start, asked "how good is this software", or',
            "  the topic is quality dimensions, indicators or software tiers:",
            "  rseng-quality-framework (the router), then follow its directory.",
        ]
    for cluster, names in CLUSTERS.items():
        lines.append(f"\n{cluster}:")
        for name in names:
            lines.append(f"- {name}: {briefs[name]}")
    return "\n".join(lines).lstrip("\n")


def rewrite(path: Path, block: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit(f"skill-directory markers missing from {path}")
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    updated = head + START + "\n\n" + block + "\n\n" + END + tail
    changed = updated != text
    path.write_text(updated, encoding="utf-8")
    return changed


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    skills = repo_root / "skills"
    rewrite(repo_root / "AGENTS.md", directory_block(skills, include_router=True))
    rewrite(
        repo_root / "skills" / "rseng-quality-framework" / "SKILL.md",
        directory_block(skills, include_router=False),
    )
    clusters = repo_root / "hooks" / "clusters.txt"
    clusters.write_text("\n".join(CLUSTERS) + "\n", encoding="utf-8")
    import json as _json

    phased = {ph: cl for ph, cl in PHASES.items()}
    assert sorted(c for cl in phased.values() for c in cl) == sorted(CLUSTERS)
    (repo_root / "hooks" / "phases.json").write_text(
        _json.dumps(phased, indent=2) + "\n", encoding="utf-8"
    )
    print("skill directory regenerated in AGENTS.md and the router skill")


if __name__ == "__main__":
    main()
