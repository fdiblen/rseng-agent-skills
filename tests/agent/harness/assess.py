"""Scoring for read-only assessment scenarios.

WHY THIS EXISTS IN THIS FORM
----------------------------
The first version asked a handful of yes/no questions with thresholds
set far below what either arm produced:

    warn(len(covered) >= 8,  "assessment breadth: 14/14 areas")
    warn(len(covered) >= 11, "assessment is comprehensive")
    warn("http" in lowered,  "assessment points to a reference")

Measured against a real run, 19 of 23 comparisons came back "both arms
pass". Only two checks moved at all, and they were the crudest in the
battery - one of them was literally whether the text contained "http".
Meanwhile the informative number, breadth, was measured as 14/14 for
the with-pack arm and 12/14 for the control and then thrown away by a
threshold both cleared.

An instrument that saturates cannot show a difference, however large
the real one is. So the continuous measures are kept continuous, and
breadth is decomposed into one check per practice area: fourteen
independent opportunities to differ instead of one that neither arm
can fail. This is not tuned to favour the pack - an area the control
raises passes for the control, and on the run that motivated the
change one agent scored identically in both arms.
"""

from __future__ import annotations

import re

# Practice areas a thorough audit of research software would raise.
# Naming the missing licence, tests and README is a floor every agent
# clears; breadth across these is where an audit either is or is not
# informed by the pack.
ASSESSMENT_AREAS = {
    "licensing": ("licen",),
    "testing": ("test", "pytest", "unittest"),
    "documentation": ("readme", "documentation", "docstring"),
    "citation": ("citation", "cff", "codemeta", "doi", "zenodo"),
    "reproducible environment": (
        "environment",
        "dependenc",
        "requirements",
        "pyproject",
        "lockfile",
        "uv.lock",
        "virtualenv",
    ),
    "version control": ("git", "version control", "commit", "gitignore"),
    "continuous integration": (
        "continuous integration",
        "ci/cd",
        " ci ",
        "github action",
        "workflow",
    ),
    "security": ("security", "secret", "credential", "vulnerab"),
    "data management": ("data management", "dataset", "data handling", "provenance"),
    "ai declaration": ("aidecl", "ai declaration", "ai usage", "ai-generated"),
    "packaging": ("packag", "module", "src layout", "installable"),
    "code quality": ("lint", "type hint", "style", "complexity", "readab"),
    "fair": ("fair", "findable", "interoperable", "reusable"),
    "contributing": ("contributing", "code of conduct", "governance"),
}

ACTIONABILITY = (
    "recommend",
    "next step",
    "should",
    "add ",
    "create ",
    "suggest",
    "priorit",
    "first",
    "start by",
)

# Concrete things an audit can tell you to add. Naming the artifact is
# a stronger signal than saying "improve documentation", and unlike a
# keyword it cannot be satisfied by prose alone.
ARTIFACT_NAMES = (
    "LICENSE",
    "CITATION.cff",
    "pyproject.toml",
    "requirements.txt",
    "README",
    "aidecl.yaml",
    ".gitignore",
    "codemeta.json",
    "CONTRIBUTING",
    "CODE_OF_CONDUCT",
    "environment.yml",
    "uv.lock",
)

# Named standards and registries. "http" was the old test, which any
# stray link satisfied; naming the standard shows the audit knows which
# one applies.
STANDARDS = (
    "fair4rs",
    "fair for research software",
    "spdx",
    "citation file format",
    "cff",
    "codemeta",
    "zenodo",
    "orcid",
    "ossf",
    "openssf",
    "semantic version",
    "semver",
    "pep 8",
    "pep8",
    "pep 621",
    "software heritage",
    "ropensci",
)

# An explicitly ordered set of recommendations: a numbered list, or
# wording that ranks the findings.
PRIORITY_MARKERS = (
    "priorit",
    "most important",
    "start with",
    "highest",
    "critical first",
    "quick win",
    "immediate",
    "short term",
    "long term",
)
NUMBERED_RE = re.compile(r"(?m)^\s*(?:\d+[.)]|#{1,6}\s*\d+[.)])\s+\S")


def areas_covered(text: str) -> list[str]:
    """Practice areas the audit actually raises."""
    lowered = (text or "").lower()
    return sorted(
        area
        for area, tokens in ASSESSMENT_AREAS.items()
        if any(token in lowered for token in tokens)
    )


def artifacts_named(text: str) -> list[str]:
    lowered = (text or "").lower()
    return sorted({name for name in ARTIFACT_NAMES if name.lower() in lowered})


def standards_named(text: str) -> list[str]:
    lowered = (text or "").lower()
    return sorted({name for name in STANDARDS if name in lowered})


def measure(text: str) -> dict:
    """Every graded quantity, kept as a number rather than a verdict."""
    covered = areas_covered(text)
    artifacts = artifacts_named(text)
    standards = standards_named(text)
    lowered = (text or "").lower()
    return {
        "areas_covered": covered,
        "areas_total": len(ASSESSMENT_AREAS),
        "breadth": len(covered) / len(ASSESSMENT_AREAS),
        "artifacts_named": artifacts,
        "artifact_count": len(artifacts),
        "standards_named": standards,
        "standard_count": len(standards),
        "prioritised": any(m in lowered for m in PRIORITY_MARKERS)
        or bool(NUMBERED_RE.search(text or "")),
        "actionable": any(t in lowered for t in ACTIONABILITY),
        "chars": len(text or ""),
    }


def emit_checks(text: str, agent: str, warn, info) -> dict:
    """Turn the measurement into per-area checks and report the rest.

    One check per practice area, so an audit that raises twelve of
    fourteen scores twelve of fourteen instead of collapsing to a
    single "comprehensive" pass that says nothing.
    """
    got = measure(text)
    covered = set(got["areas_covered"])
    for area in sorted(ASSESSMENT_AREAS):
        warn(area in covered, f"[{agent}] audit raises {area}")

    warn(
        got["artifact_count"] >= 3,
        f"[{agent}] audit names concrete artifacts to add "
        f"({got['artifact_count']}: {', '.join(got['artifacts_named'][:6]) or 'none'})",
    )
    warn(
        got["standard_count"] >= 1,
        f"[{agent}] audit cites a named standard "
        f"({', '.join(got['standards_named'][:4]) or 'none'})",
    )
    warn(got["prioritised"], f"[{agent}] audit orders its findings")
    warn(got["actionable"], f"[{agent}] audit gives actionable next steps")

    # Reported, not asserted: the graded values behind the checks.
    info(
        f"[{agent}] audit breadth {len(covered)}/{got['areas_total']} "
        f"({100 * got['breadth']:.0f}%), {got['chars']} chars"
    )
    return got
