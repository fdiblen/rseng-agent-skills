"""PreToolUse gate: plan before you write, keep practice current while
you write.

Before the first file write, .rseng-agent-skills-coverage.md must carry a
complete, ledger-backed Start section and a Throughout section (the
cross-cutting skills begin at the beginning). Once development is
under way (several approved writes), the During section falls due as
well. Writes to the coverage worklog itself always pass - it is the
escape from the gate, by design. Opt out with .rseng-agent-skills-relaxed.
"""

import pathlib
import sys

import phase_lib
import tool_event

data = phase_lib.read_event()
phase_lib.record_hook("gate")

# Ask tool_event rather than naming Claude's tools. hook_wiring ships this
# gate to codex and gemini too, where the write tools are apply_patch,
# shell, write_file and replace - none of which matched the old literal
# list, so the gate allowed every write, never recorded one, and the
# write counter it feeds left the Stop-time audit switched off as well.
if not tool_event.is_write(data.get("tool_name") or ""):
    sys.exit(0)

targets = tool_event.targets(data) or [""]
target_path = pathlib.Path(targets[0])

# The enforcement infrastructure protects itself - agents may not
# edit the hook scripts, their data files, or the machine-written
# session records. Checked BEFORE the opt-out below: the agent is
# allowed to create .rseng-agent-skills-relaxed, so testing the opt-out
# first let it switch the gate off and then rewrite the gate.
name = target_path.name
parts = target_path.parts
if (any(d in parts for d in phase_lib.AGENT_DIRS) and "rseng" in parts) or name in (
    ".rseng-agent-skills-usage.log",
    ".rseng-agent-skills-writes",
    ".rseng-hooks-fired.log",
):
    print(
        "rseng-agent-skills: this file records what the session did, so the "
        "session does not edit it. Nothing is wrong - write the project's "
        "own files instead.",
        file=sys.stderr,
    )
    sys.exit(2)

if pathlib.Path(".rseng-agent-skills-relaxed").exists():
    sys.exit(0)

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
    # A blocked write is the pack working, but a bystander sees only a
    # refusal. Say whose job it is to resolve, and how to switch it off, so
    # a first run does not read as a fault.
    print(
        "rseng-agent-skills: holding this write until the start-of-work steps "
        "are recorded. Expected on a first run - the agent resolves it and "
        "nothing is needed from you. (.rseng-agent-skills-coverage.md is "
        "always writable; add an empty .rseng-agent-skills-relaxed file to "
        "turn the gate off.)\n- " + "\n- ".join(problems),
        file=sys.stderr,
    )
    sys.exit(2)

phase_lib.record_write()
sys.exit(0)
