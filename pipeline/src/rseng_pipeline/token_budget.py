"""Token-budget report and gate for the pack's context surface.

Skills cost context twice: every skill's name+description is loaded
into the session for routing (the always-paid surface), and a skill's
body is paid on each consultation. This module measures both with a
chars/4 estimate (close enough for budgeting; no tokenizer
dependency), prints a report, and fails when a budget is exceeded so
context bloat is caught in CI, not in sessions.

Usage:
    python -m rseng_pipeline.token_budget          # report + gate
    python -m rseng_pipeline.token_budget --report # report only
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

# Budgets (tokens, chars/4 estimate). The description budget leaves
# room under the Agent Skills spec cap (1024 chars ~ 256 tokens);
# the routing surface is what every session pays before any work.
DESCRIPTION_BUDGET = 200
BODY_BUDGET = 3_500
ROUTING_SURFACE_BUDGET = 13_000
SESSION_CONTEXT_BUDGET = 1_100


def tokens(text: str) -> int:
    return len(text) // 4


def measure(repo_root: Path) -> dict:
    skills: list[dict[str, Any]] = []
    for skill_md in sorted(repo_root.glob("skills/*/SKILL.md")):
        text = skill_md.read_text(encoding="utf-8")
        fm = re.match(r"(?s)^---\n(.*?)\n---\n", text)
        if fm is None:
            raise SystemExit(
                f"{skill_md}: no frontmatter block - run skill_lint for detail"
            )
        meta = yaml.safe_load(fm.group(1)) or {}
        if "description" not in meta:
            raise SystemExit(f"{skill_md}: frontmatter has no description")
        skills.append(
            {
                "name": skill_md.parent.name,
                "description_tokens": tokens(str(meta["description"])),
                "body_tokens": tokens(text[fm.end() :]),
            }
        )
    routing = sum(s["description_tokens"] + tokens(s["name"]) for s in skills)
    context = repo_root / "hooks" / "session-context.md"
    return {
        "skills": skills,
        "routing_surface_tokens": routing,
        "session_context_tokens": tokens(context.read_text(encoding="utf-8"))
        if context.is_file()
        else 0,
    }


def problems(report: dict) -> list[str]:
    out = []
    for s in report["skills"]:
        if s["description_tokens"] > DESCRIPTION_BUDGET:
            out.append(
                f"{s['name']}: description ~{s['description_tokens']} tokens "
                f"(budget {DESCRIPTION_BUDGET}) - every session pays this"
            )
        if s["body_tokens"] > BODY_BUDGET:
            out.append(
                f"{s['name']}: body ~{s['body_tokens']} tokens "
                f"(budget {BODY_BUDGET}) - paid per consultation"
            )
    if report["routing_surface_tokens"] > ROUTING_SURFACE_BUDGET:
        out.append(
            f"routing surface ~{report['routing_surface_tokens']} tokens "
            f"(budget {ROUTING_SURFACE_BUDGET})"
        )
    if report["session_context_tokens"] > SESSION_CONTEXT_BUDGET:
        out.append(
            f"session-context.md ~{report['session_context_tokens']} tokens "
            f"(budget {SESSION_CONTEXT_BUDGET})"
        )
    return out


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    report = measure(repo_root)
    n = len(report["skills"])
    total_desc = sum(s["description_tokens"] for s in report["skills"])
    total_body = sum(s["body_tokens"] for s in report["skills"])
    print(
        f"token budget: {n} skills; routing surface "
        f"~{report['routing_surface_tokens']:,} tokens "
        f"(descriptions ~{total_desc:,}, mean ~{total_desc // n}); "
        f"bodies ~{total_body:,} total (mean ~{total_body // n:,}); "
        f"session context ~{report['session_context_tokens']:,}"
    )
    worst = sorted(report["skills"], key=lambda s: -s["description_tokens"])[:5]
    print(
        "largest descriptions: "
        + ", ".join(f"{s['name']} ~{s['description_tokens']}" for s in worst)
    )
    found = problems(report)
    if found and "--report" not in sys.argv:
        print("over budget:")
        for p in found:
            print(f"- {p}")
        raise SystemExit(1)
    if found:
        print(f"(report-only: {len(found)} items over budget)")


if __name__ == "__main__":
    main()
