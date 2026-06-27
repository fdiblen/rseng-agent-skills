"""PreToolUse gate: plan before you write.

Blocks Write/Edit (exit 2) until .rseng-agent-skills-coverage.md exists with
a Start section covering every Start-phase cluster - the beginning-
of-task practice pass (planning, data, reuse/licensing, stack) has
to happen before the first file is written. Also requires at least
one rseng-* skill consultation. Opt out with .rseng-agent-skills-relaxed.
"""

import json
import pathlib
import sys

data = json.load(sys.stdin)
if pathlib.Path(".rseng-agent-skills-relaxed").exists():
    sys.exit(0)
if data.get("tool_name") not in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
    sys.exit(0)

phases_file = pathlib.Path(__file__).parent / "phases.json"
start_clusters = []
if phases_file.is_file():
    start_clusters = json.loads(phases_file.read_text(encoding="utf-8")).get(
        "Start", []
    )

coverage = pathlib.Path(".rseng-agent-skills-coverage.md")
text = coverage.read_text(encoding="utf-8").lower() if coverage.is_file() else ""
absent = [c for c in start_clusters if c.lower() not in text]

ledger = pathlib.Path(".rseng-agent-skills-usage.log")
consulted = ledger.is_file() and any(
    line.startswith("rseng-")
    for line in ledger.read_text(encoding="utf-8").splitlines()
)

if consulted and "## start" in text and not absent:
    sys.exit(0)

problems = []
if not consulted:
    problems.append(
        "consult the relevant rseng-* skills first (router: "
        "rseng-quality-framework)"
    )
if "## start" not in text or absent:
    problems.append(
        "write the Start section of .rseng-agent-skills-coverage.md: for each "
        "Start-phase cluster record 'applied: <skills and decisions>' "
        "or 'n/a: <reason>'. Still unaddressed: "
        + ("; ".join(absent) if absent else "all Start clusters")
    )
print(
    "rseng-agent-skills gate - before writing files: " + " AND ".join(problems)
    + ". (Relax with a .rseng-agent-skills-relaxed file.)",
    file=sys.stderr,
)
sys.exit(2)
