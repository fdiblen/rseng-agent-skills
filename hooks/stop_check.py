"""Stop hook: one honest compliance pass before finishing.

Blocks the first stop (exit 2) when the session consulted fewer
than two rseng-* skills, asking for either consultation or a stated
reason. Never blocks twice (stop_hook_active) and respects
.rseng-agent-skills-relaxed.
"""

import json
import pathlib
import sys

data = json.load(sys.stdin)
if data.get("stop_hook_active") or pathlib.Path(".rseng-agent-skills-relaxed").exists():
    sys.exit(0)
ledger = pathlib.Path(".rseng-agent-skills-usage.log")
entries = set()
if ledger.is_file():
    entries = {
        line.strip()
        for line in ledger.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("rseng-")
    }
if len(entries) >= 2:
    sys.exit(0)
print(
    f"rseng-agent-skills check before finishing: only {len(entries)} rseng-* "
    "skill(s) were consulted this session. If the work touched research "
    "software, consult the relevant skills now (router: "
    "rseng-quality-framework) and verify aidecl.yaml is current; if the "
    "skills genuinely do not apply, say so briefly and finish.",
    file=sys.stderr,
)
sys.exit(2)
