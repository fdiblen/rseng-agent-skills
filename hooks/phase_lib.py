"""Shared state and parsing for the phased skill-enforcement hooks.

The three hooks (gate, prompt status, stop audit) all reason about the
same evidence: phases.json (phase -> cluster -> skills), the coverage
worklog the agent maintains, and the consultation ledger written by
the Skill-tool hook. A coverage claim of "applied" only counts when at
least one rseng-* skill named in that cluster's entry also appears in
the ledger - self-report has to be backed by an actual consultation.
"""

import json
import os
import pathlib
import re
import sys

COVERAGE = pathlib.Path(".rseng-agent-skills-coverage.md")
LEDGER = pathlib.Path(".rseng-agent-skills-usage.log")
WRITES = pathlib.Path(".rseng-agent-skills-writes")


def load_phases(script_dir):
    f = pathlib.Path(script_dir) / "phases.json"
    if not f.is_file():
        return {}
    data = json.loads(f.read_text(encoding="utf-8"))
    return {
        phase: (clusters if isinstance(clusters, dict) else {c: [] for c in clusters})
        for phase, clusters in data.items()
    }


def coverage_text():
    if not COVERAGE.is_file():
        return ""
    return COVERAGE.read_text(encoding="utf-8", errors="replace").lower()


def consulted_skills():
    if not LEDGER.is_file():
        return set()
    return {
        line.strip()
        for line in LEDGER.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip().startswith("rseng-")
    }


def write_count():
    if not WRITES.is_file():
        return 0
    return len(WRITES.read_text(encoding="utf-8", errors="replace").splitlines())


def record_write():
    """Never raises: a read-only checkout must not traceback on the success
    path, after the agent did everything the gate asked."""
    try:
        with WRITES.open("a", encoding="utf-8") as f:
            f.write("w\n")
    except OSError:
        pass


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
    rest n/a: <reason>")."""
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
        if s not in ledger and not mentions(s, text) and s not in covered
    )


def is_project_file(path, root):
    """Does this path belong to the project rather than its tooling?

    Judged on the path RELATIVE to the project: an absolute path can run
    through a dot-directory that has nothing to do with the project, and
    that must not hide the whole tree. Shared with the adapter self-check
    so the two cannot drift - they already had, and the drift let a
    dependency's tests under .venv/ satisfy the tests requirement.
    """
    try:
        parts = (
            pathlib.Path(path).resolve().relative_to(pathlib.Path(root).resolve()).parts
        )
    except ValueError:
        return False
    return not any(part.startswith(".") for part in parts) and not (
        {"node_modules", "site-packages"} & set(parts)
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
    source_files = [
        p
        for p in files
        if p.suffix
        in (
            ".py",
            ".R",
            ".jl",
            ".sh",
            ".ipynb",
            ".c",
            ".h",
            ".cpp",
            ".cu",
            ".cuh",
            ".f",
            ".f90",
            ".F90",
        )
    ]
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
            s for s in rule["skills"] if s not in ledger and not _waived(s, text)
        ]
        if missing:
            unmet.append((rule["name"], evidence, missing))
    return unmet


def mentions(name, text):
    """Is this exact skill named in the text?

    Plain substring matching made one skill name a prefix of another:
    'rseng-data-management' sits inside 'rseng-data-management-plans', so
    dispositioning the plans skill silently dispositioned the other one too.
    \\b does not help - a hyphen is itself a word boundary - so the
    neighbours are excluded explicitly.
    """
    return re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", text) is not None


def _waived(skill, text):
    """A waiver is any worklog line mentioning the skill together with
    'n/a' - both documented orders ('n/a: skill - reason' and
    'skill: n/a - reason') count."""
    for line in text.splitlines():
        if mentions(skill, line) and "n/a" in line:
            return True
    return False


def cluster_applied(phases, cluster, text, ledger):
    """True when this cluster is recorded applied and ledger-backed."""
    all_clusters = [c for cl in phases.values() for c in cl]
    seg = _segment(text, cluster, all_clusters)
    if seg is None or "applied" not in seg:
        return False
    return bool(set(re.findall(r"rseng-[a-z0-9-]+", seg)) & ledger)


AGENT_DIRS = (".claude", ".agents", ".cursor", ".codex", ".gemini")


def gitignore_gap(root):
    """Agent working dirs present but not ignored: the generated
    project would commit local agent config/session state."""
    present = [d for d in AGENT_DIRS if (root / d).is_dir()]
    if not present:
        return None
    gi = root / ".gitignore"
    text = gi.read_text(encoding="utf-8") if gi.is_file() else ""
    missing = [d for d in present if d not in text]
    if missing:
        return (
            ".gitignore does not cover the agent working directories "
            f"present here ({', '.join(missing)}) - add them (plus .env "
            "plus .rseng-agent-skills-* session records and .rseng-backup-* "
            "directories); commit shared agent "
            "config back explicitly only if the team intends it"
        )
    return None


# Whether the proactive layer actually ran, rather than merely being
# installed. A config on disk is not evidence that the agent executed
# it - codex in particular installs the hooks without them ever being
# seen to fire. Each hook records itself here.
HOOKS_FIRED = pathlib.Path(".rseng-hooks-fired.log")

# Opt-in. The log answers one question - did the agent execute the
# hooks, or were they only installed - and nothing in a normal project
# consumes it. Writing it unconditionally dropped a growing file into
# every repository the pack was installed in; a few hundred lines had
# accumulated here before anyone asked what it was. Set
# RSENG_HOOK_TELEMETRY=1 when you want the record.
TELEMETRY_ENV = "RSENG_HOOK_TELEMETRY"


def read_event():
    """The hook payload on stdin, or {} if it cannot be read.

    A hook runs inside someone's coding session. An agent that changes its
    event shape, sends nothing, or sends something that is not JSON must
    not produce a Python traceback in that session - the hook should just
    find nothing to act on and get out of the way. Same reasoning as
    record_hook below: a hook must not fail on its own plumbing.
    """
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    # Normalise the two fields every caller reaches into. Guarding only the
    # top-level shape left `"tool_input": "a string"` and a numeric
    # tool_name raising AttributeError deep inside four different hooks -
    # and in Claude Code a PreToolUse hook that exits non-zero-but-not-2
    # shows its stderr to the user and stops enforcing, so the traceback
    # was both the alarming message and a silent loss of the gate.
    if not isinstance(data.get("tool_input"), dict):
        data["tool_input"] = {}
    if not isinstance(data.get("tool_name"), str):
        data["tool_name"] = ""
    return data


def record_hook(name):
    """Note that a hook ran, when telemetry is switched on.

    Never raises: a hook must not fail because its own bookkeeping did.
    """
    if os.environ.get(TELEMETRY_ENV) != "1":
        return
    try:
        with HOOKS_FIRED.open("a", encoding="utf-8") as handle:
            handle.write(f"{name}\n")
    except OSError:
        pass
