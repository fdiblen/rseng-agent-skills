"""UserPromptSubmit hook: one-line live status of the phased practice
worklog, so the current phase stays salient on every turn. Never
blocks; prints nothing when there is nothing to say."""

import pathlib
import sys

import phase_lib

phase_lib.record_hook("phase_status")
if pathlib.Path(".rseng-agent-skills-relaxed").exists():
    sys.exit(0)

phases = phase_lib.load_phases(pathlib.Path(__file__).parent)
if not phases:
    sys.exit(0)

text = phase_lib.coverage_text()
ledger = phase_lib.consulted_skills()

parts = []
for phase in phases:
    n = len(phase_lib.phase_problems(phases, phase, text, ledger))
    parts.append(f"{phase}: {'ok' if n == 0 else f'{n} open'}")
crosscut = next(iter(phases.get("Throughout", {}).values()), [])
unopened = [s for s in crosscut if s not in ledger]
inventory = phase_lib.all_skills(phases)
open_dispositions = len(phase_lib.undispositioned(phases, text, ledger))
line = (
    "rseng-agent-skills phases [" + "; ".join(parts) + "] - "
    f"{len(ledger)} skills consulted, {phase_lib.write_count()} writes, "
    f"{len(inventory) - open_dispositions}/{len(inventory)} skills dispositioned."
)
if unopened:
    line += " Cross-cutting skills not yet opened: " + ", ".join(unopened) + "."
unmet = phase_lib.unmet_signals(pathlib.Path(__file__).parent, ledger, text)
if unmet:
    line += (
        " Relevant-but-unconsulted: "
        + "; ".join(f"{', '.join(m)} ({name})" for name, _e, m in unmet[:4])
        + "."
    )
print(line)
sys.exit(0)
