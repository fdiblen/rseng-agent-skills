"""Stop hook: the output must carry the practice, whether or not
skills were opened.

When the session produced code, block the first stop attempt with a
concrete list of missing practice artifacts. The agent then adds
them - or states, briefly and honestly, why an item does not apply
to this tier of work - and finishes. Never blocks twice
(stop_hook_active); .rseng-agent-skills-relaxed disables it.
"""

import json
import pathlib
import sys

data = json.load(sys.stdin)
if data.get("stop_hook_active") or pathlib.Path(".rseng-agent-skills-relaxed").exists():
    sys.exit(0)

cwd = pathlib.Path(".")
code = [
    p
    for ext in ("*.py", "*.R", "*.jl", "*.js", "*.ts", "*.c", "*.cpp", "*.f90")
    for p in cwd.rglob(ext)
    if ".claude" not in p.parts and not p.parts[0].startswith(".")
]
if not code:
    sys.exit(0)

missing = []
if not list(cwd.glob("README*")):
    missing.append("README with purpose and how-to-run")
if not list(cwd.glob("LICENSE*")):
    missing.append("LICENSE (unlicensed code legally blocks all reuse)")
if not pathlib.Path("aidecl.yaml").is_file():
    missing.append("aidecl.yaml AI usage declaration")
if not pathlib.Path("CITATION.cff").is_file():
    missing.append("CITATION.cff citation metadata")
if not [p for p in cwd.rglob("test_*.py") if ".claude" not in p.parts] and not list(
    cwd.rglob("tests")
):
    missing.append("tests (at least a smoke/reference-case check)")
if not (
    list(cwd.glob("pyproject.toml"))
    or list(cwd.glob("uv.lock"))
    or list(cwd.glob("requirements*.txt"))
    or list(cwd.glob("environment*.y*ml"))
    or any("# /// script" in p.read_text(encoding="utf-8", errors="ignore") for p in code[:10] if p.suffix == ".py")
):
    missing.append("environment/dependency declaration (uv + pyproject or PEP 723)")

ledger = pathlib.Path(".rseng-agent-skills-usage.log")
consulted = ledger.is_file() and any(
    line.startswith("rseng-") for line in ledger.read_text(encoding="utf-8").splitlines()
)
if not consulted:
    missing.append("consult the relevant rseng-* skills (router: rseng-quality-framework)")

if not missing:
    sys.exit(0)
print(
    "rseng-agent-skills quality check - this project is missing practice "
    "artifacts. Add each item, or state briefly why it does not apply "
    "to this tier of work, then finish:\n- " + "\n- ".join(missing),
    file=sys.stderr,
)
sys.exit(2)
