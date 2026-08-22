"""Which agents and tools can actually run here.

On PATH is not the same as runnable. A wheel can import while the
binary it bundles will not execute, and a prebuilt CLI can be present
but refused by the loader - both were reported as available until the
probes started actually starting them.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from harness.config import AGENT_COMMANDS, RECORDS_DIR, SANDBOX_ROOT


def agent_available(agent: str) -> bool:
    return shutil.which(AGENT_COMMANDS[agent]("probe")[0]) is not None


def _binary_runs(binary: str) -> tuple[bool, str]:
    """Does this CLI actually start?

    On PATH is not the same as executable. A prebuilt binary the
    loader refuses is still on PATH; the probe called one ready and
    the failure only surfaced two sessions into a run, as
    "rc=127: Could not start dynamically linked executable". This is
    the same lesson the tool probe already learned.
    """
    try:
        probe = subprocess.run(
            [binary, "--version"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except FileNotFoundError:
        return False, f"{binary} not executable"
    except OSError as error:
        return False, f"{binary} cannot start: {error}"
    except subprocess.TimeoutExpired:
        # Starting at all is the question; a slow --version still
        # proves the loader accepted the binary.
        return True, "ready"
    output = f"{probe.stdout}\n{probe.stderr}"
    # 127 is the shell/loader "cannot execute" code. A non-zero exit
    # from the CLI's own argument parsing is not a launch failure, so
    # only the loader signature is treated as unavailable.
    if probe.returncode == 127 or "dynamically linked executable" in output:
        first = next(
            (ln.strip() for ln in output.splitlines() if ln.strip()),
            "cannot execute",
        )
        return False, f"{binary} will not start: {first[:90]}"
    return True, "ready"


def agent_readiness(agent: str) -> tuple[bool, str]:
    """Can this agent actually run a headless session here?

    A CLI on PATH is necessary but not sufficient - gemini refuses to
    start on a Workspace account without a cloud project, and finding
    that out only from a failed session wastes a run.
    """
    binary = AGENT_COMMANDS[agent]("probe")[0]
    if shutil.which(binary) is None:
        return False, f"{binary} not on PATH"

    runs, why = _binary_runs(binary)
    if not runs:
        return False, why

    if agent == "gemini":
        if os.environ.get("GEMINI_API_KEY"):
            return True, "GEMINI_API_KEY set"
        if os.environ.get("GOOGLE_CLOUD_PROJECT"):
            return True, "GOOGLE_CLOUD_PROJECT set"
        accounts = Path.home() / ".gemini" / "google_accounts.json"
        if accounts.is_file():
            try:
                active = json.loads(accounts.read_text(encoding="utf-8")).get(
                    "active", ""
                )
            except (OSError, json.JSONDecodeError):
                active = ""
            if active and not active.endswith("@gmail.com"):
                return False, (
                    f"workspace account {active} needs GOOGLE_CLOUD_PROJECT "
                    "or GEMINI_API_KEY"
                )
        return True, "oauth credentials present"

    if agent == "codex" and not (Path.home() / ".codex").is_dir():
        return False, "~/.codex missing (not logged in)"
    if agent == "claude" and not (Path.home() / ".claude").is_dir():
        return False, "~/.claude missing (not logged in)"
    return True, "ready"


def detect_agents() -> list[tuple[str, bool, str]]:
    """Every known agent with whether it can run and why not."""
    return [(a, *agent_readiness(a)) for a in sorted(AGENT_COMMANDS)]


OPTIONAL_TOOLS = {
    "bandit": "security scan (regex fallback otherwise)",
    "ruff": "lint findings and syntax check",
    "coverage": "statement coverage",
    "pytest": "test execution (unittest fallback otherwise)",
}


def detect_tools() -> list[tuple[str, bool, str]]:
    """Tools that can RUN, not merely import.

    A wheel can import fine while the binary it bundles cannot
    execute; an import probe reported one as installed while every
    check it backed silently came back unmeasured.
    """
    try:
        import checks as check_registry

        runs = check_registry._tool_runs
    except Exception:  # noqa: BLE001 - fall back to a local probe

        def runs(module: str) -> bool:
            try:
                probe = subprocess.run(
                    [sys.executable, "-m", module, "--version"],
                    capture_output=True,
                    timeout=60,
                    check=False,
                )
                return probe.returncode == 0
            except (OSError, subprocess.TimeoutExpired):
                return False

    return [
        (module, runs(module), purpose) for module, purpose in OPTIONAL_TOOLS.items()
    ]


def preflight(targets: list[str]) -> list[str]:
    """Print what the environment can and cannot measure, and return
    the targets that will actually run."""
    print("environment")
    runnable = []
    for agent, ok, why in detect_agents():
        selected = agent in targets
        mark = "run " if (ok and selected) else "skip"
        note = why if ok else f"unavailable: {why}"
        if selected and not ok:
            note = f"SKIPPED - {why}"
        print(f"  [{mark}] {agent:<12} {note}")
        if ok and selected:
            runnable.append(agent)
    for tool, ok, purpose in detect_tools():
        print(f"  [{'ok  ' if ok else 'miss'}] {tool:<12} {purpose}")
    print(f"  sandboxes: {SANDBOX_ROOT}")
    print(f"  records:   {RECORDS_DIR}")
    if not runnable:
        print("  no runnable agent - nothing to do")
    return runnable
