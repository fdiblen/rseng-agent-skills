"""Keeping each session\'s generated project for later comparison.

Both arms are kept. Archiving only the control left every claim about
what the pack produced resting on numbers with no artefact behind them.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from harness.config import KEEP, RECORDS_DIR, SESSIONS_FILE

ARCHIVE_STORE = RECORDS_DIR / "archives"


def _session_recorded(label: str) -> bool:
    """Did this label actually produce a session record?"""
    runlog = RECORDS_DIR / SESSIONS_FILE
    if not runlog.is_file():
        return False
    for line in runlog.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            if json.loads(line).get("label") == label:
                return True
        except json.JSONDecodeError:
            continue
    return False


def archive_baseline(sandbox: Path, label: str) -> Path | None:
    """Keep a session's generated project for comparison.

    Both arms are kept, under .agent-sandboxes/archives/<arm>/<cell>/,
    replacing any previous run of the same cell so the store always
    reflects the latest run. Archiving only the control left every
    claim about what the pack produced resting on numbers with no
    artefact behind them. Agent working directories and virtualenvs are
    left out - what matters is the code the agent produced.
    """
    if not sandbox.is_dir():
        return None
    if not _session_recorded(label):
        # Archiving runs from a `finally:`, so a launch that never
        # started still reached it: copilot failed with rc=127 and the
        # store gained an "output" directory holding the seeded file
        # and the installed pack, as though the agent had produced them.
        print(
            f"  [archive] {label}: no session recorded, nothing to archive", flush=True
        )
        return None
    # The arm is in the label. Reading it from a module-level global
    # coupled this to whatever the runner had last set.
    baseline = label.startswith("baseline/")
    cell = label.replace("baseline/", "").strip("/").replace("/", "__") or "unlabelled"
    slug = f"{'baseline' if baseline else 'with-pack'}/{cell}"
    destination = ARCHIVE_STORE / slug
    try:
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True, exist_ok=True)
        for item in sandbox.iterdir():
            # Agent working dirs, virtualenvs, and artefacts the HARNESS
            # itself left behind (its diagnostic sweep writes .mypy_cache
            # and .coverage; report_token_usage writes .rseng-tokens.json).
            # Archiving those as "control output" would attribute the
            # harness's own files to the agent.
            if item.name in (
                ".agent-config",
                ".claude",
                ".agents",
                ".cursor",
                ".codex",
                ".gemini",
                ".venv",
                ".test-venv",
                "__pycache__",
                ".git",
                ".mypy_cache",
                ".pytest_cache",
                ".ruff_cache",
                ".coverage",
                ".rseng-tokens.json",
            ):
                continue
            # A virtualenv is not agent output, whatever it is called.
            # One named `venv` slipped past the name list above and put
            # 581 MB of third-party packages into the archive.
            if item.is_dir() and (item / "pyvenv.cfg").is_file():
                continue
            target = destination / item.name
            if item.is_dir():
                shutil.copytree(
                    item,
                    target,
                    dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                )
            else:
                shutil.copy2(item, target)
    except OSError as error:
        print(f"  [archive] could not archive {label}: {error}", flush=True)
        return None
    arm = "control" if baseline else "with-pack"
    print(f"  [archive] {arm} output kept at: {destination}", flush=True)
    return destination


def _finish_sandbox(sandbox: Path) -> None:
    if not KEEP:
        shutil.rmtree(sandbox, ignore_errors=True)
        return
    print(f"\n  sandbox kept at: {sandbox}")
    for path in sorted(sandbox.rglob("*")):
        if (
            path.is_file()
            and ".claude" not in path.parts
            and ".fake-home" not in path.parts
        ):
            print(f"    {path.relative_to(sandbox)}  ({path.stat().st_size}B)")
