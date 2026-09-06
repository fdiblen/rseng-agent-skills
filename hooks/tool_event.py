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

# Tools that hand a shell command to the system. Whether the call is a
# write depends on the command, not the tool: `ls` and `cat > app.py`
# arrive through the same one.
SHELL_TOOLS = {"shell", "exec_command", "exec", "run_shell_command", "bash"}

# Commands that change the filesystem. Deliberately generous - a missed
# write switches the whole enforcement layer off for the session, while a
# false positive costs one explained pause.
MUTATING = {
    "cp",
    "mv",
    "rm",
    "rmdir",
    "mkdir",
    "touch",
    "truncate",
    "dd",
    "ln",
    "install",
    "chmod",
    "chown",
    "tee",
    "patch",
    "sponge",
    "shred",
    "unzip",
    "tar",
    "rsync",
    "curl",
    "wget",
    "git",
    "npm",
    "pip",
    "uv",
    "make",
    "just",
    "cargo",
    "go",
    "poetry",
    "gh",
}
# Multiplexers whose read-only subcommands are the ones agents run most.
# Gating `git status` would make the pack unbearable; gating `git apply`
# is the whole point.
READ_SUBCOMMANDS = {
    "git": {
        "status",
        "log",
        "diff",
        "show",
        "ls-files",
        "ls-tree",
        "rev-parse",
        "rev-list",
        "cat-file",
        "blame",
        "grep",
        "describe",
        "shortlog",
        "config",
        "remote",
        "branch",
        "tag",
        "whatchanged",
        "reflog",
        "for-each-ref",
        "check-ignore",
        "merge-base",
        "name-rev",
        "var",
    },
}

# Editors and interpreters only count when told to write in place.
INPLACE = re.compile(r"\b(?:sed|perl|ruby)\b[^|;&]*\s-\w*i\b")
# Any redirection that creates or appends to a file, but not 2>&1.
REDIRECT = re.compile(r"(?<![0-9&>])>>?(?!\s*&)")

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


def shell_writes(command: object) -> bool:
    """Does this shell command change the filesystem?

    Claude's Bash tool was in neither the tool list nor the hook matcher,
    so `cat > app.py <<EOF` was never gated, never counted as a write, and
    left the stop-time audit believing the session had written nothing.
    Deleting the write counter went the same way.
    """
    text = str(command or "")
    if not text.strip():
        return False
    if REDIRECT.search(text) or INPLACE.search(text):
        return True
    try:
        words = shlex.split(text)
    except ValueError:
        words = text.split()
    # Check the head of every segment, so `ls && rm -rf x` is a write.
    expect_command = True
    pending = ""
    for word in words:
        if word in ("|", "||", "&&", ";", "&"):
            expect_command = True
            continue
        if expect_command:
            name = word.rsplit("/", 1)[-1]
            if name in MUTATING:
                pending = name
                expect_command = False
                continue
            # env VAR=x cmd, sudo cmd, nohup cmd: keep looking.
            expect_command = name in ("env", "sudo", "nohup", "time", "xargs")
            pending = ""
        elif pending:
            # First non-flag word after a multiplexer is its subcommand.
            if not word.startswith("-"):
                reads = READ_SUBCOMMANDS.get(pending)
                if reads is None or word not in reads:
                    return True
                pending = ""
    # A multiplexer with no subcommand at all (`git`) prints usage.
    return bool(pending) and pending not in READ_SUBCOMMANDS


def is_write_event(event: dict) -> bool:
    """Is this tool call a write, judged from the whole payload?

    Shell tools are the reason this exists: the tool name alone cannot
    tell `git status` from `rm -rf`.
    """
    tool = str(event.get("tool_name") or "").lower()
    if tool in SHELL_TOOLS:
        tool_input = event.get("tool_input") or {}
        if isinstance(tool_input, str):
            return shell_writes(tool_input)
        if not isinstance(tool_input, dict):
            return False
        for key in ("command", "cmd", "input", "arguments"):
            value = tool_input.get(key)
            if isinstance(value, str):
                return shell_writes(value)
            if isinstance(value, list):
                return shell_writes(" ".join(str(v) for v in value))
        # A shell payload with no command we recognise but naming a file
        # outright: treat it as a write. Guessing "read" is the expensive
        # direction here - it switches the gate off for that call.
        return bool(targets(event))
    return is_write(tool)


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
    if tool in SHELL_TOOLS:
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
