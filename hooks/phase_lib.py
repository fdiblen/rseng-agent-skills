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


def all_skills(phases):
    return {s for cl in phases.values() for skills in cl.values() for s in skills}


def undispositioned(phases, text, ledger):
    """Skills with no disposition: not consulted (ledger), not named
    in the worklog, and not covered by a cluster-level n/a. A cluster
    segment containing "n/a" disposes every skill in that cluster at
    once ("n/a: <reason>" for a whole cluster, or "applied: X, Y;
    rest n/a: <reason>"), keeping the full-inventory rule without
    67 individual lines."""
    all_clusters = [c for cl in phases.values() for c in cl]
    covered = set()
    for clusters in phases.values():
        for cluster, skills in clusters.items():
            seg = _segment(text, cluster, all_clusters)
            if seg is not None and "n/a" in seg:
                covered.update(skills)
    return sorted(
        s
        for s in all_skills(phases)
        if s not in ledger and s not in text and s not in covered
    )


def _project_files(root, limit=4000):
    files = []
    for p in root.rglob("*"):
        if len(files) >= limit:
            break
        if p.is_file() and not any(
            part.startswith(".") or part == "node_modules" for part in p.parts
        ):
            files.append(p)
    return files


def unmet_signals(script_dir, ledger, text, root=None):
    """Signal rules whose evidence exists in the project but whose
    skills were neither consulted nor explicitly waived (an 'n/a'
    naming the skill in the coverage worklog). Returns
    (rule_name, evidence, missing_skills) tuples."""
    import re

    signals_file = pathlib.Path(script_dir) / "signals.json"
    if not signals_file.is_file():
        return []
    rules = json.loads(signals_file.read_text(encoding="utf-8"))
    root = pathlib.Path(root or ".")
    files = _project_files(root)
    source_files = [p for p in files if p.suffix in (".py", ".R", ".jl", ".sh", ".ipynb")]
    unmet = []
    for rule in rules:
        evidence = None
        for pattern in rule.get("patterns", []):
            hits = [p for p in files if p.match(pattern)]
            if hits:
                evidence = str(hits[0])
                break
        if evidence is None:
            for regex in rule.get("content", []):
                pat = re.compile(regex)
                for p in source_files[:60]:
                    try:
                        body = p.read_text(encoding="utf-8", errors="ignore")[:200_000]
                    except OSError:
                        continue
                    if pat.search(body):
                        evidence = f"{p} matches /{regex}/"
                        break
                if evidence:
                    break
        if evidence is None:
            continue
        missing = [
            s
            for s in rule["skills"]
            if s not in ledger and not _waived(s, text)
        ]
        if missing:
            unmet.append((rule["name"], evidence, missing))
    return unmet


def _waived(skill, text):
    """A waiver is any worklog line mentioning the skill together with
    'n/a' - both documented orders ('n/a: skill - reason' and
    'skill: n/a - reason') count."""
    for line in text.splitlines():
        if skill in line and "n/a" in line:
            return True
    return False


def cluster_applied(phases, cluster, text, ledger):
    """True when this cluster is recorded applied and ledger-backed."""
    all_clusters = [c for cl in phases.values() for c in cl]
    seg = _segment(text, cluster, all_clusters)
    if seg is None or "applied" not in seg:
        return False
    return bool(set(re.findall(r"rseng-[a-z0-9-]+", seg)) & ledger)
