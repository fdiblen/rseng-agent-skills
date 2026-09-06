"""PostToolUse hook: when a just-touched file matches a relevance
signal whose skills have not been consulted, say so NOW - at the moment
the relevant work is happening, not at Stop time. Signals carrying
severity "privacy" produce an explicit warning whenever the file is
touched, consulted or not: the user must know sensitive data is being
processed. Awareness nudge only - never blocks.

Agent-neutral: the tool names and payload shapes differ per agent, so
which files a call touched is worked out by tool_event rather than by
testing for claude's Write/Edit/Read and claude's "file_path".
"""

import json
import pathlib
import re
import sys

import phase_lib
import tool_event

data = phase_lib.read_event()
phase_lib.record_hook("signal_nudge")
tool = data.get("tool_name") or ""
if not (tool_event.is_write(tool) or tool_event.is_read(tool)):
    sys.exit(0)
tool_input = data.get("tool_input") or {}
touched = tool_event.targets(data)
if not touched:
    sys.exit(0)

# Opening a skill counts as consulting it. Only claude and cursor have a
# Skill tool to hook, so without this the ledger stays empty forever on
# every other agent - and the gate refuses every write on an empty ledger.
phase_lib.record_consultation(touched)

signals_file = pathlib.Path(__file__).parent / "signals.json"
if not signals_file.is_file():
    sys.exit(0)
rules = json.loads(signals_file.read_text(encoding="utf-8"))
ledger = phase_lib.consulted_skills()
text = phase_lib.coverage_text()


def _matches(rule, path, body):
    """A rule fires on the filename, or on what the file contains."""
    if any(path.match(p) for p in (rule.get("patterns") or [])):
        return True
    return bool(body) and any(
        re.search(expr, body) for expr in (rule.get("content") or [])
    )


pending = []
privacy_hit = None
path = pathlib.Path(touched[0])
for candidate in touched:
    where = pathlib.Path(candidate)
    contents = tool_event.body(data, candidate)
    for rule in rules:
        if not _matches(rule, where, contents):
            continue
        if rule.get("severity") == "privacy":
            privacy_hit = rule["name"]
            path = where
        # Read-side touches only warn for privacy signals; consultation
        # nudges stay write-side so ordinary reads are not noisy.
        if tool_event.is_read(tool):
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
                        "each before going further, by invoking it or reading "
                        "its SKILL.md (or record a reasoned n/a in "
                        ".rseng-agent-skills-coverage.md): " + ", ".join(pending)
                    ),
                }
            }
        )
    )
sys.exit(0)
