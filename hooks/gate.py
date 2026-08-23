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
phase_lib.record_hook("gate")
if pathlib.Path(".rseng-agent-skills-relaxed").exists():
    sys.exit(0)
if data.get("tool_name") not in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
    sys.exit(0)

tool_input = data.get("tool_input") or {}
target = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
target_path = pathlib.Path(target)

# The enforcement infrastructure protects itself - agents may not
# edit the hook scripts, their data files, or the machine-written
# session records. Fail-closed here is safe: these writes are never
# part of legitimate project work.
name = target_path.name
parts = target_path.parts
if (".claude" in parts and "rseng" in parts) or name in (
    ".rseng-agent-skills-usage.log",
    ".rseng-agent-skills-writes",
):
    print(
        "rseng-agent-skills gate - the enforcement infrastructure (hook scripts, "
        "their data, the consultation ledger and the write counter) is "
        "not writable by the session; it records what happened, it is "
        "not project content.",
        file=sys.stderr,
    )
    sys.exit(2)

# Only the coverage worklog (agent-authored by design) passes the
# gate freely; .rseng-agent-skills-relaxed may be created deliberately.
if name in (".rseng-agent-skills-coverage.md", ".rseng-agent-skills-relaxed"):
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
