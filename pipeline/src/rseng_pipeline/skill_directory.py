"""Generate the grouped skill directory in AGENTS.md and the router.

One source of truth for "which skill covers what": the cluster map
below plus each skill's frontmatter brief. Rewrites the blocks between
the skill-directory markers in AGENTS.md and in
skills/rseng-quality-framework/SKILL.md, so the two lists can never
drift apart. Fails loudly when a skill is missing from the map.

Usage: python -m rseng_pipeline.skill_directory
"""

from __future__ import annotations

import json
from pathlib import Path

import frontmatter

from .adapters import _brief

START = "<!-- skill-directory:start (generated - do not edit by hand) -->"
END = "<!-- skill-directory:end -->"

# Primary phase per cluster: when in a task each practice area is
# considered first (revisited whenever relevant).
#: The graph, the clusters and the routing rules live in data/ rather
#: than inline. They are a hand-maintained table, not logic - keeping
#: them here made this the largest "code" file in the repo while only
#: three of its 622 lines were executable.
DATA = Path(__file__).parent / "data"


def _load(name):
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


PHASES: dict[str, list[str]] = _load("phases")

# Skills exercised across the whole lifecycle, from before the first
# file is written until the final stop: they also belong to their home
# clusters, but the hooks track them as a standing obligation.
# Relevance signals: when a project contains these files (patterns) or
# its sources match these regexes (content), the mapped skills ARE
# relevant - the hooks require each to be consulted or explicitly
# waived with a reasoned n/a. High-precision rules only: a false
# "relevant" costs an agent a pointless consultation on every project.
SIGNALS: list[dict] = _load("signals")

# The router is every session's entry point and stays relevant for
# the whole task; it lives outside the clusters but inside the
# Throughout phase so the enforcement inventory covers all skills.
# Skills with no characteristic file, so no signal can fire for them.
# They are routed by phase instead - a session-level obligation rather
# than a file-touch trigger. Declared explicitly with the reason,
# because the alternative is inventing a pattern that matches
# everything: a signal that fires on every *.py file would nudge on
# every project and teach the agent to ignore signals.
#
# main() asserts every skill is either signalled or listed here, so a
# new skill cannot arrive with no proactive route at all.
PHASE_ONLY: dict[str, str] = _load("phase_only")

ROUTER = "rseng-quality-framework"

THROUGHOUT: list[str] = _load("throughout")

CLUSTERS: dict[str, list[str]] = _load("clusters")


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
    import json as _json

    assert sorted(c for cl in PHASES.values() for c in cl) == sorted(CLUSTERS)
    all_skills = {s for skills in CLUSTERS.values() for s in skills}
    unknown = [s for s in THROUGHOUT if s not in all_skills | {ROUTER}]
    assert not unknown, f"THROUGHOUT names unknown skills: {unknown}"
    phased = {ph: {c: CLUSTERS[c] for c in cl} for ph, cl in PHASES.items()}
    phased["Throughout"] = {"Cross-cutting practices": THROUGHOUT}
    # Every skill on disk must belong to at least one phase - a skill
    # outside the phase map escapes the disposition and coverage
    # checks entirely.
    on_disk = {
        d.name for d in (repo_root / "skills").iterdir() if (d / "SKILL.md").is_file()
    }
    in_phases = {s for cl in phased.values() for ss in cl.values() for s in ss}
    unphased = sorted(on_disk - in_phases)
    assert not unphased, f"skills in no phase: {unphased}"
    (repo_root / "hooks" / "phases.json").write_text(
        _json.dumps(phased, indent=2) + "\n", encoding="utf-8"
    )
    for rule in SIGNALS:
        bad = [s for s in rule["skills"] if s not in all_skills]
        assert not bad, f"SIGNALS rule {rule['name']!r} names unknown skills: {bad}"

    # Every skill needs a proactive route: a file signal, or an
    # explicit statement that no file can indicate it. Without this a
    # new skill joins the pack, is routed only by the generic phase
    # nudge, and is never consulted by anything that notices what the
    # agent is actually doing.
    names = [rule["name"] for rule in SIGNALS]
    duplicates = sorted({n for n in names if names.count(n) > 1})
    assert not duplicates, f"SIGNALS has duplicate rule name(s): {duplicates}"

    # Only rules that can actually fire count as a route. Rules with
    # neither patterns nor content match nothing, and counting them as
    # coverage is how four skills came to be "signalled" by a rule the
    # hook silently skipped.
    signalled = {
        s
        for rule in SIGNALS
        if rule.get("patterns") or rule.get("content")
        for s in rule["skills"]
    }
    stray = sorted(s for s in PHASE_ONLY if s not in on_disk)
    assert not stray, f"PHASE_ONLY names skills that do not exist: {stray}"
    overlap = sorted(signalled & set(PHASE_ONLY))
    assert not overlap, f"skills both signalled and declared phase-only: {overlap}"
    unrouted = sorted(on_disk - signalled - set(PHASE_ONLY))
    assert not unrouted, (
        f"{len(unrouted)} skill(s) have no file signal and no stated reason "
        f"for having none: {unrouted}. Add a high-precision rule to SIGNALS, "
        "or list the skill in PHASE_ONLY with why no file can indicate it."
    )
    (repo_root / "hooks" / "signals.json").write_text(
        _json.dumps(SIGNALS, indent=2) + "\n", encoding="utf-8"
    )
    print("skill directory regenerated in AGENTS.md and the router skill")


if __name__ == "__main__":
    main()
