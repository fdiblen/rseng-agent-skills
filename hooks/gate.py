"""PreToolUse gate: no file writes before consulting the skills.

Blocks Write/Edit (exit 2) until .rseng-agent-skills-usage.log records at
least one rseng-* skill consultation in this project. Opt out by
creating a .rseng-agent-skills-relaxed file.
"""

import json
import pathlib
import sys

data = json.load(sys.stdin)
if pathlib.Path(".rseng-agent-skills-relaxed").exists():
    sys.exit(0)
if data.get("tool_name") not in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
    sys.exit(0)
ledger = pathlib.Path(".rseng-agent-skills-usage.log")
entries = set()
if ledger.is_file():
    entries = {
        line.strip()
        for line in ledger.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("rseng-")
    }
if entries:
    sys.exit(0)
print(
    "rseng-agent-skills gate: before writing files, invoke the rseng-* skills "
    "relevant to this task (unsure which: invoke rseng-quality-framework "
    "and follow its directory). The gate opens after the first "
    "consultation. To relax this gate for the project, create a "
    ".rseng-agent-skills-relaxed file.",
    file=sys.stderr,
)
sys.exit(2)
