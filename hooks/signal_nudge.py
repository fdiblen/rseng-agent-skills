"""PostToolUse hook on Write/Edit/Read: when a just-touched file
matches a relevance signal whose skills have not been consulted, say
so NOW - at the moment the relevant work is happening, not at Stop
time. Signals carrying severity "privacy" produce an explicit warning
whenever the file is touched, consulted or not: the user must know
sensitive data is being processed. Awareness nudge only - never
blocks."""

import json
import pathlib
import sys

import phase_lib

data = json.load(sys.stdin)
tool = data.get("tool_name")
if tool not in ("Write", "Edit", "MultiEdit", "NotebookEdit", "Read"):
    sys.exit(0)
tool_input = data.get("tool_input") or {}
target = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
if not target:
    sys.exit(0)

signals_file = pathlib.Path(__file__).parent / "signals.json"
if not signals_file.is_file():
    sys.exit(0)
rules = json.loads(signals_file.read_text(encoding="utf-8"))
ledger = phase_lib.consulted_skills()
text = phase_lib.coverage_text()
path = pathlib.Path(target)

pending = []
privacy_hit = None
for rule in rules:
    if not any(path.match(p) for p in rule.get("patterns", [])):
        continue
    if rule.get("severity") == "privacy":
        privacy_hit = rule["name"]
    # Read-side touches only warn for privacy signals; consultation
    # nudges stay write-side so ordinary reads are not noisy.
    if tool == "Read":
        continue
    for skill in rule["skills"]:
        if (
            skill not in ledger
            and not phase_lib._waived(skill, text)
            and skill not in pending
        ):
            pending.append(skill)

if privacy_hit:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        f"PRIVACY WARNING: {path.name} matches "
                        f"'{privacy_hit}' - this session is processing "
                        "data that may identify people. Tell the user "
                        "explicitly, apply rseng-data-management and "
                        "rseng-regulatory-compliance handling (minimize, "
                        "never commit, aggregate before sharing), and "
                        "record the decision in the worklog."
                    ),
                }
            }
        )
    )
    sys.exit(0)

if pending:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        f"{path.name} makes these skills relevant - consult "
                        "each with the Skill tool before going further (or "
                        "record a reasoned n/a in .rseng-agent-skills-coverage.md): "
                        + ", ".join(pending)
                    ),
                }
            }
        )
    )
sys.exit(0)
