"""PostToolUse hook on Write/Edit: when a just-written file matches a
relevance signal whose skills have not been consulted, say so NOW -
at the moment the relevant work is happening, not at Stop time.
Awareness nudge only - never blocks."""

import json
import pathlib
import sys

import phase_lib

data = json.load(sys.stdin)
if data.get("tool_name") not in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
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
for rule in rules:
    if not any(path.match(p) for p in rule.get("patterns", [])):
        continue
    for skill in rule["skills"]:
        if (
            skill not in ledger
            and not phase_lib._waived(skill, text)
            and skill not in pending
        ):
            pending.append(skill)

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
