"""PreToolUse gate: plan before you write, keep practice current while
you write.

Before the first file write, .rseng-agent-skills-coverage.md must carry a
complete, ledger-backed Start section and a Throughout section (the
cross-cutting skills begin at the beginning). Once development is
under way (several approved writes), the During section falls due as
well. Writes to the coverage worklog itself always pass - it is the
escape from the gate, by design. The user can opt out by creating
.rseng-agent-skills-relaxed themselves; the session cannot create it.
"""

import pathlib
import sys

import phase_lib
import tool_event

RELAXED = ".rseng-agent-skills-relaxed"

data = phase_lib.read_event()
phase_lib.record_hook("gate")

# Ask tool_event rather than naming any agent's tools. This gate ships to
# codex and gemini too, whose write tools are apply_patch, shell,
# write_file and replace; and it takes the whole event, because Claude's
# Bash tool appears in no write list at all - so `cat > app.py <<EOF`
# walked straight past, never incremented the write counter, and left the
# Stop-time audit believing the session had written nothing.
if not tool_event.is_write_event(data):
    sys.exit(0)

# EVERY target, not just the first. A shell call naming the coverage
# worklog first passed freely and carried whatever else it touched with
# it - one allowed path shielded the rest of the command.
paths = [pathlib.Path(t) for t in (tool_event.targets(data) or [""])]

# The enforcement infrastructure protects itself - agents may not
# edit the hook scripts, their data files, or the machine-written
# session records. Checked BEFORE the opt-out below, or testing the
# opt-out first would let a session switch the gate off and then
# rewrite the gate.
RECORDS = (
    ".rseng-agent-skills-usage.log",
    ".rseng-agent-skills-writes",
    ".rseng-hooks-fired.log",
)


def protected(path):
    parts = path.parts
    return (
        any(d in parts for d in phase_lib.AGENT_DIRS) and "rseng" in parts
    ) or path.name in RECORDS


if any(protected(p) for p in paths):
    print(
        "rseng-agent-skills: this file records what the session did, so the "
        "session does not edit it. Nothing is wrong - write the project's "
        "own files instead.",
        file=sys.stderr,
    )
    sys.exit(2)

# The opt-out belongs to the person, not to the session being gated. When
# the agent could create it too, the cheapest way to satisfy the gate was
# to delete the gate: one Write, and the phases, the ledger and the
# Stop-time audit were all off for the rest of the session.
if any(p.name == RELAXED for p in paths):
    print(
        f"rseng-agent-skills: {RELAXED} turns this pack's checks off, so it "
        "is the user's to create, not the session's. Ask them to run "
        f"`touch {RELAXED}` if they want the checks relaxed here.",
        file=sys.stderr,
    )
    sys.exit(2)

if pathlib.Path(RELAXED).exists():
    sys.exit(0)

# The coverage worklog is agent-authored by design, so it passes freely -
# but only when it is the ONLY thing the call touches.
if paths and all(p.name == ".rseng-agent-skills-coverage.md" for p in paths):
    sys.exit(0)

phases = phase_lib.load_phases(pathlib.Path(__file__).parent)
text = phase_lib.coverage_text()
ledger = phase_lib.consulted_skills()

DURING_AFTER_WRITES = 8

problems = []
if not ledger:
    problems.append(
        "no rseng-* skill has been consulted yet - open the relevant "
        "skills first (the Skill tool where there is one, otherwise read "
        "their SKILL.md; router: rseng-quality-framework)"
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
        f"always writable; if you want the gate off, `touch {RELAXED}` "
        "yourself - the agent is not allowed to.)\n- " + "\n- ".join(problems),
        file=sys.stderr,
    )
    sys.exit(2)

phase_lib.record_write()
sys.exit(0)
