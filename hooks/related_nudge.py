"""PostToolUse hook on Skill: whenever a skill is consulted, surface
its related skills so the agent can check whether a neighbor applies
to the task at hand. Awareness nudge only - never blocks."""

import json
import pathlib
import sys

import phase_lib

data = phase_lib.read_event()
phase_lib.record_hook("related_nudge")
# The dict lookup below needs a hashable key, and the payload shape is
# the host's to choose: a list here raised "unhashable type: 'list'".
skill = (data.get("tool_input") or {}).get("skill", "")
if not isinstance(skill, str):
    sys.exit(0)
related_file = pathlib.Path(__file__).parent / "related.json"
if not skill or not related_file.is_file():
    sys.exit(0)
related = json.loads(related_file.read_text(encoding="utf-8")).get(skill)
if not related:
    sys.exit(0)
lines = "; ".join(f"{name} ({reason})" for name, reason in related.items())
print(
    json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    f"Skills related to {skill} - check whether any "
                    f"applies to the current task: {lines}"
                ),
            }
        }
    )
)
sys.exit(0)
