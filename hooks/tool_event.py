"""Reading a tool call the same way whatever agent made it.

Every agent names its tools and shapes its payloads differently:

    claude   Write / Edit / MultiEdit / NotebookEdit / Read
             {"file_path": "...", "content": "..."}
    codex    apply_patch / shell / exec_command
             a "*** Begin Patch / *** Add File: x.py" body, or argv
    cursor   its own edit tools, again with its own field names

The hooks used to test `tool_name in ("Write", "Edit", ...)` and read
`tool_input["file_path"]`, so they fired for claude and were silent for
every other agent - which is why one agent was nudged toward skills all
session and the others never were. This module turns any of those into
the same two answers: which files were touched, and what was written.
"""

from __future__ import annotations

import json
import re
import shlex

# Tools that create or change files, per agent. A name not listed here
# is treated as a read, which only matters for privacy warnings.
WRITE_TOOLS = {
    # claude
    "write",
    "edit",
    "multiedit",
    "notebookedit",
    # codex
    "apply_patch",
    "applypatch",
    "shell",
    "exec_command",
    "exec",
    # gemini
    "write_file",
    "replace",
    "run_shell_command",
    # cursor and friends
    "edit_file",
    "create_file",
    "search_replace",
}
READ_TOOLS = {"read", "read_file", "view", "cat", "read_many_files"}

# `*** Add File: path`, `*** Update File: path`, `*** Delete File: path`
PATCH_TARGET = re.compile(
    r"^\*\*\*\s+(?:Add|Update|Delete|Move to)\s+File:\s*(.+?)\s*$", re.MULTILINE
)
# A bare path mentioned in a shell command: conservative on purpose,
# since a false path produces a nudge about a file nobody touched.
SHELL_PATH = re.compile(r"(?:^|\s|['\"><])([\w./-]+\.[A-Za-z0-9]{1,8})(?=$|\s|['\"])")

PATCH_BODY = "*** Begin Patch"


def is_write(tool_name: object) -> bool:
    # Coerce rather than assume: these are public helpers reached from a
    # payload the agent host controls, and a numeric tool_name used to
    # raise AttributeError on .lower().
    return str(tool_name or "").lower() in WRITE_TOOLS


def is_read(tool_name: object) -> bool:
    return str(tool_name or "").lower() in READ_TOOLS


def targets(event: dict) -> list[str]:
    """Every file this tool call appears to touch.

    Explicit fields first; only when an agent gives none do we look
    inside a patch body or a command line.
    """
    tool_input = event.get("tool_input") or {}
    if isinstance(tool_input, str):
        tool_input = {"input": tool_input}

    named = []
    for key in ("file_path", "notebook_path", "path", "filename", "target_file"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            named.append(value)
    if named:
        return named

    blob = ""
    for key in ("input", "patch", "command", "cmd", "content", "arguments"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            blob = value
            break
        if isinstance(value, list) and value:
            blob = " ".join(str(v) for v in value)
            break
    if not blob:
        blob = json.dumps(tool_input)

    if PATCH_BODY in blob or "*** Add File" in blob:
        found = PATCH_TARGET.findall(blob)
        if found:
            return found

    tool = (event.get("tool_name") or "").lower()
    if tool in ("shell", "exec_command", "exec", "run_shell_command"):
        try:
            words = shlex.split(blob)
        except ValueError:
            words = blob.split()
        # Only tokens that look like a file this command writes to.
        return [w for w in words if SHELL_PATH.fullmatch(w)]
    return []


def body(event: dict, path: str = "") -> str:
    """What was written, for the rules that match on content.

    Falls back to reading the file when the agent's payload does not
    carry it - codex sends a patch, not the resulting file.
    """
    max_scan = 200_000
    tool_input = event.get("tool_input") or {}
    if isinstance(tool_input, dict):
        for key in ("content", "new_string", "input", "patch"):
            value = tool_input.get(key)
            if isinstance(value, str) and value:
                return value[:max_scan]
    if path:
        try:
            with open(path, encoding="utf-8", errors="ignore") as handle:
                return handle.read(max_scan)
        except OSError:
            return ""
    return ""
