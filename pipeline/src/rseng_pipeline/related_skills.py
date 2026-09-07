"""Skill-relations graph: renders a "Related skills" section into
every SKILL.md and emits hooks/related.json for the consultation
nudge hook.

The map is curated here (single source). Every skill must have an
entry and every edge must name an existing skill - unknown or missing
names fail loudly. Rendering is idempotent (marker block) and must run
as the LAST step after any content regeneration, since source-fed
SKILL.md files are rewritten by the adapter pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path

BEGIN = "<!-- related-skills:begin -->"
END = "<!-- related-skills:end -->"

# skill -> {neighbor: when the neighbor becomes relevant}
#: The graph, the clusters and the routing rules live in data/ rather
#: than inline. They are a hand-maintained table, not logic - keeping
#: them here made this the largest "code" file in the repo while only
#: three of its 622 lines were executable.
DATA = Path(__file__).parent / "data"


def _load(name):
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


RELATED: dict[str, list[str]] = _load("related")


def _block(related: dict[str, str]) -> str:
    lines = [
        BEGIN,
        "",
        "## Related skills",
        "",
        "Check whether any of these applies before moving on:",
        "",
    ]
    lines += [f"- {name} - {reason}" for name, reason in related.items()]
    lines += ["", END]
    return "\n".join(lines)


def render(repo_root: Path) -> None:
    # Take the universe from disk, not from CLUSTERS. Deriving it from the
    # cluster map meant a skill missing from BOTH maps was invisible to this
    # assertion: it rendered "sections for 67 skills", exited 0, and left the
    # new one with no related-skills block and no entry in related.json.
    # Three documents promise this fails loudly; now it does.
    known = {p.parent.name for p in (repo_root / "skills").glob("rseng-*/SKILL.md")}
    missing = sorted(known - set(RELATED))
    assert not missing, f"skills without a RELATED entry: {missing}"
    unknown = sorted(set(RELATED) - known)
    assert not unknown, f"RELATED names unknown skills: {unknown}"
    for skill, related in RELATED.items():
        bad = sorted(set(related) - known)
        assert not bad, f"{skill}: unknown neighbors {bad}"
        assert skill not in related, f"{skill}: self-edge"
        path = repo_root / "skills" / skill / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        block = _block(related)
        if BEGIN in text:
            head, rest = text.split(BEGIN, 1)
            _, tail = rest.split(END, 1)
            text = head + block + tail
        else:
            anchor = "\n---\n\nGuidance based on"
            if anchor in text:
                head, tail = text.split(anchor, 1)
                text = head.rstrip() + "\n\n" + block + "\n" + anchor + tail
            else:
                text = text.rstrip() + "\n\n" + block + "\n"
        path.write_text(text, encoding="utf-8")
    (repo_root / "hooks" / "related.json").write_text(
        json.dumps(RELATED, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    render(repo_root)
    print(f"related-skills sections rendered for {len(RELATED)} skills")


if __name__ == "__main__":
    main()
