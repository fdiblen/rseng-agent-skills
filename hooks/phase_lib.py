"""Shared state and parsing for the phased skill-enforcement hooks.

The three hooks (gate, prompt status, stop audit) all reason about the
same evidence: phases.json (phase -> cluster -> skills), the coverage
worklog the agent maintains, and the consultation ledger written by
the Skill-tool hook. A coverage claim of "applied" only counts when at
least one rseng-* skill named in that cluster's entry also appears in
the ledger - self-report has to be backed by an actual consultation.
"""

import json
import pathlib
import re

COVERAGE = pathlib.Path(".rseng-agent-skills-coverage.md")
LEDGER = pathlib.Path(".rseng-agent-skills-usage.log")
WRITES = pathlib.Path(".rseng-agent-skills-writes")


def load_phases(script_dir):
    f = pathlib.Path(script_dir) / "phases.json"
    if not f.is_file():
        return {}
    data = json.loads(f.read_text(encoding="utf-8"))
    return {
        phase: (
            clusters
            if isinstance(clusters, dict)
            else {c: [] for c in clusters}
        )
        for phase, clusters in data.items()
    }


def coverage_text():
    if not COVERAGE.is_file():
        return ""
    return COVERAGE.read_text(encoding="utf-8").lower()


def consulted_skills():
    if not LEDGER.is_file():
        return set()
    return {
        line.strip()
        for line in LEDGER.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("rseng-")
    }


def write_count():
    if not WRITES.is_file():
        return 0
    return len(WRITES.read_text(encoding="utf-8").splitlines())


def record_write():
    with WRITES.open("a", encoding="utf-8") as f:
        f.write("w\n")


def _segment(text, cluster, all_clusters):
    """Text from this cluster's first mention to the next cluster or heading."""
    start = text.find(cluster.lower())
    if start < 0:
        return None
    boundaries = [len(text)]
    for other in all_clusters:
        if other == cluster:
            continue
        pos = text.find(other.lower(), start + len(cluster))
        if pos > start:
            boundaries.append(pos)
    heading = text.find("\n## ", start)
    if heading > start:
        boundaries.append(heading)
    return text[start : min(boundaries)]


def phase_problems(phases, phase, text, ledger):
    """Problems blocking this phase's section, as agent-actionable strings."""
    clusters = phases.get(phase, {})
    if not clusters:
        return []
    if f"## {phase.lower()}" not in text:
        return [
            f"'## {phase}' section missing from {COVERAGE.name} - record "
            "each cluster as 'applied: <rseng-* skills and decisions>' or "
            "'n/a: <one-line reason>': " + "; ".join(clusters)
        ]
    all_clusters = [c for cl in phases.values() for c in cl]
    problems = []
    for cluster, skills in clusters.items():
        seg = _segment(text, cluster, all_clusters)
        hint = ", ".join(skills[:3]) if skills else "rseng-quality-framework"
        if seg is None:
            problems.append(
                f"{phase} / {cluster}: not recorded - add 'applied: ...' "
                f"or 'n/a: <reason>' (candidate skills: {hint})"
            )
            continue
        applied = "applied" in seg
        na = "n/a" in seg
        if not applied and not na:
            problems.append(
                f"{phase} / {cluster}: mentioned but neither 'applied:' "
                f"nor 'n/a: <reason>' recorded (candidate skills: {hint})"
            )
        elif applied:
            claimed = set(re.findall(r"rseng-[a-z0-9-]+", seg))
            if not claimed:
                problems.append(
                    f"{phase} / {cluster}: 'applied' must name the rseng-* "
                    f"skills used (candidate skills: {hint})"
                )
            elif not claimed & ledger:
                problems.append(
                    f"{phase} / {cluster}: claimed applied, but none of "
                    "the named skills appear in the consultation ledger - "
                    "actually open them with the Skill tool "
                    f"({', '.join(sorted(claimed)[:3])})"
                )
    return problems


def cluster_applied(phases, cluster, text, ledger):
    """True when this cluster is recorded applied and ledger-backed."""
    all_clusters = [c for cl in phases.values() for c in cl]
    seg = _segment(text, cluster, all_clusters)
    if seg is None or "applied" not in seg:
        return False
    return bool(set(re.findall(r"rseng-[a-z0-9-]+", seg)) & ledger)
