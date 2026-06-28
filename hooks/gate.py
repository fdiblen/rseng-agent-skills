"""PreToolUse gate: plan before you write, keep practice current while
you write.

Before the first file write, .rseng-agent-skills-coverage.md must carry a
complete, ledger-backed Start section and a Throughout section (the
cross-cutting skills begin at the beginning). Once development is
under way (several approved writes), the During section falls due as
well. Writes to the coverage worklog itself always pass - it is the
escape from the gate, by design. Opt out with .rseng-agent-skills-relaxed.
"""

import json
import pathlib
import sys

import phase_lib

data = json.load(sys.stdin)
if pathlib.Path(".rseng-agent-skills-relaxed").exists():
    sys.exit(0)
if data.get("tool_name") not in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
    sys.exit(0)

tool_input = data.get("tool_input") or {}
target = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
if pathlib.Path(target).name.startswith(".rseng-agent-skills"):
    sys.exit(0)

phases = phase_lib.load_phases(pathlib.Path(__file__).parent)
text = phase_lib.coverage_text()
ledger = phase_lib.consulted_skills()

DURING_AFTER_WRITES = 8

problems = []
if not ledger:
    problems.append(
        "no rseng-* skill has been consulted yet - open the relevant "
        "skills with the Skill tool first (router: rseng-quality-framework)"
    )
problems += phase_lib.phase_problems(phases, "Start", text, ledger)
problems += phase_lib.phase_problems(phases, "Throughout", text, ledger)
if phase_lib.write_count() >= DURING_AFTER_WRITES:
    during = phase_lib.phase_problems(phases, "During", text, ledger)
    if during:
        problems.append(
            "development is well under way - record the During practice "
            "pass now, not at the end:"
        )
        problems += during

if problems:
    print(
        "rseng-agent-skills gate - resolve before writing project files "
        "(.rseng-agent-skills-coverage.md itself is always writable):\n- "
        + "\n- ".join(problems),
        file=sys.stderr,
    )
    sys.exit(2)

phase_lib.record_write()
sys.exit(0)
