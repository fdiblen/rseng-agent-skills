"""Triage suggestions for structural upstream changes.

When the classifier finds a NEW page, suggest which skill should own it
by comparing the page's keywords and related_pages against the pages each
skill already owns. When nothing scores, propose a new skill instead.
"""

from __future__ import annotations

from dataclasses import dataclass

import frontmatter

from .parser import parse_page
from .references import skill_page_ids


@dataclass(frozen=True)
class MappingSuggestion:
    page_id: str
    skill: str | None  # None means: nothing fits, propose a new skill
    score: int
    reasons: tuple[str, ...]


def _keywords_of(blob: bytes) -> set[str]:
    meta = frontmatter.loads(blob.decode("utf-8", errors="replace")).metadata
    words: set[str] = set()
    for keyword in meta.get("keywords") or []:
        words.update(str(keyword).lower().split())
    return words


def suggest_mapping(
    path: str,
    blob: bytes,
    taxonomy: dict,
    known_keywords: dict[str, set[str]],
) -> MappingSuggestion:
    """Score every skill for one new page.

    Scoring: +3 for each related_pages reference to a page a skill owns,
    +1 for each keyword word shared with the skill's existing pages.
    ``known_keywords`` maps page_id -> keyword word set for existing pages.
    """
    record = parse_page(blob.decode("utf-8", errors="replace"), path)
    related = {pid for ids in record.related_pages.values() for pid in ids}
    new_words = _keywords_of(blob)

    best: tuple[int, str | None, tuple[str, ...]] = (0, None, ())
    for skill, entry in taxonomy.items():
        owned = set(skill_page_ids(entry))
        score = 0
        reasons: list[str] = []
        overlap = related & owned
        if overlap:
            score += 3 * len(overlap)
            reasons.append(f"related_pages -> {', '.join(sorted(overlap))}")
        shared = new_words & {
            word for pid in owned for word in known_keywords.get(pid, set())
        }
        if shared:
            score += len(shared)
            reasons.append(f"keywords: {', '.join(sorted(shared)[:5])}")
        if score > best[0]:
            best = (score, skill, tuple(reasons))

    score, skill, reasons = best
    if score == 0:
        return MappingSuggestion(
            page_id=record.page_id,
            skill=None,
            score=0,
            reasons=("no keyword or related_pages overlap; consider a new skill",),
        )
    return MappingSuggestion(
        page_id=record.page_id, skill=skill, score=score, reasons=reasons
    )


def render_suggestions(suggestions: list[MappingSuggestion]) -> str:
    if not suggestions:
        return ""
    lines = ["## Taxonomy suggestions for new pages", ""]
    for suggestion in suggestions:
        target = (
            f"map to `{suggestion.skill}` (score {suggestion.score})"
            if suggestion.skill
            else "no existing skill fits - propose a NEW skill"
        )
        lines.append(f"- `{suggestion.page_id}`: {target}")
        for reason in suggestion.reasons:
            lines.append(f"    - {reason}")
    lines.append("")
    return "\n".join(lines) + "\n"
