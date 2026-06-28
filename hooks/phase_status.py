"""UserPromptSubmit hook: one-line live status of the phased practice
worklog, so the current phase stays salient on every turn. Never
blocks; prints nothing when there is nothing to say."""

import pathlib
import sys

import phase_lib

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
line = (
    "rseng-agent-skills phases [" + "; ".join(parts) + "] - "
    f"{len(ledger)} skills consulted, {phase_lib.write_count()} writes."
)
if unopened:
    line += " Cross-cutting skills not yet opened: " + ", ".join(unopened) + "."
print(line)
sys.exit(0)
