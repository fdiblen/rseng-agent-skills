"""Paths, environment and the agent command table.

One place for the values every part of the harness needs, so a module
can be imported without pulling in the whole runner.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

RECORDS_DIR = REPO / ".agent-sandboxes"
SESSIONS_FILE = "agent-test-sessions.jsonl"
LEGACY_SESSIONS_FILE = "token-usage.jsonl"
SANDBOX_ROOT = Path(
    os.environ.get("RSENG_AGENT_SANDBOX_ROOT")
    or Path(tempfile.gettempdir()) / "rseng-agent-sandboxes"
)
CLI = REPO / "installer" / "dist" / "cli.js"
VERBOSE = os.environ.get("RSENG_AGENT_VERBOSE") == "1"
KEEP = os.environ.get("RSENG_AGENT_KEEP") == "1"
TARGETS = [
    a.strip()
    for a in os.environ.get("RSENG_AGENT_TARGETS", "auto").split(",")
    if a.strip()
]
AGENT_COMMANDS = {
    "claude": lambda prompt: [
        "claude",
        "-p",
        prompt,
        "--output-format",
        "stream-json",
        "--verbose",
        "--dangerously-skip-permissions",
    ],
    "codex": lambda prompt: [
        "codex",
        "exec",
        "--skip-git-repo-check",
        "--dangerously-bypass-approvals-and-sandbox",
        # Codex reviews hooks at startup and will not run untrusted
        # ones; in exec mode that review has nowhere to go, so the
        # pack's hooks were installed and silently never fired. The
        # flag is documented for "automation that already vets hook
        # sources", which is what a sandbox built by this harness is.
        "--dangerously-bypass-hook-trust",
        prompt,
    ],
    "gemini": lambda prompt: [
        "gemini",
        "-p",
        prompt,
        "--approval-mode",
        "yolo",
        "-e",
        "none",
    ],
    "antigravity": lambda prompt: [
        "agy",
        "--prompt",
        prompt,
        "--yolo",
    ],
    "copilot": lambda prompt: [
        "copilot",
        "-p",
        prompt,
        "--allow-all-tools",
        "--allow-all-urls",
        "--no-color",
    ],
}
LAST_RUN: dict = {}
PRE_RUN: dict = {}
TOKEN_WARN_BUDGET = 3_000_000


def pack_version() -> str:
    """The installed pack's version, so a record says what it tested."""
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO), "describe", "--tags", "--always", "--dirty"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return (out.stdout or "").strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


# Sandbox contents before the agent starts, so its output can be told
# apart from the scenario seed and the installed pack.
PRE_RUN: dict = {}

# What the last launched session did: exit code, wall clock, whether it
# timed out. Written by the runner, read when the record is assembled.
LAST_RUN: dict = {}
