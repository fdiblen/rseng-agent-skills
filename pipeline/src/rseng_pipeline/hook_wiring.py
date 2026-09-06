"""One definition of the proactive layer, emitted per agent.

The nudging hooks were written as Claude Code hooks and shipped only to
claude. Every other agent received the skills and the context file but
nothing that noticed what it was doing, so one agent was steered toward
skills all session and the rest were left to remember on their own -
which is exactly what the consultation counts showed.

Codex takes the same shape of hook configuration as Claude Code
(`hooks.json`, the same event names, the same `hookSpecificOutput`
wire), so the two differ only in which tool names count as a write.
Keeping both in this one table is what stops them drifting apart.
"""

from __future__ import annotations

import json
from pathlib import Path

# The scripts the hooks run. Copied next to the config so an install is
# self-contained and does not reach back into the pack.
HOOK_SCRIPTS = (
    "gate.py",
    "session_start.py",
    "phase_lib.py",
    "phase_status.py",
    "quality_check.py",
    "related_nudge.py",
    "signal_nudge.py",
    "tool_event.py",
    "phases.json",
    "related.json",
    "signals.json",
    "session-context.md",
)

# Which tool names mean "a file was written" for each agent, as a hook
# matcher. Claude matches tool names directly; codex names its tools
# shell / apply_patch / exec_command.
# Bash is in the write matchers because a shell is a write tool: the
# matcher only decides whether the hook RUNS, and tool_event.shell_writes
# then decides whether the command actually changes anything. Leaving it
# out meant `cat > app.py <<EOF` was never seen by the gate at all.
WRITE_MATCHERS = {
    "claude": "Write|Edit|MultiEdit|NotebookEdit|Bash",
    "codex": "apply_patch|shell|exec_command",
    "cursor": "Write|Edit|MultiEdit|edit_file|create_file|search_replace|Bash",
    "gemini": "write_file|replace|edit|run_shell_command",
}
READ_MATCHERS = {
    "claude": "Write|Edit|MultiEdit|NotebookEdit|Bash|Read",
    "codex": "apply_patch|shell|exec_command|read_file",
    "cursor": "Write|Edit|MultiEdit|edit_file|create_file|Bash|Read|read_file",
    "gemini": "write_file|replace|edit|run_shell_command|read_file",
}
# The tool an agent uses to pull in a skill, if it has one. Codex has
# no skill tool - it reads SKILL.md files - so it gets no matcher here
# and its related-skill nudge hangs off the read side instead.
SKILL_MATCHERS = {
    "claude": "Skill",
    "cursor": "Skill",
}

# Agents whose hook system was CONFIRMED to take this configuration,
# each from the tool itself rather than from documentation about it:
#
#   claude  the existing hooks, in use
#   codex   event names, hooks.json and the hookSpecificOutput wire
#           read out of the shipped binary
#   gemini  `gemini hooks migrate` converts Claude Code hooks, and the
#           bundle carries the same events and additionalContext
#
# cursor is NOT here. Its hook format is only mentioned indirectly, in
# codex's migration code, and cursor-agent is not installed to check
# against - so shipping a config for it would be a guess. copilot
# exposes no hook mechanism at all. Both still get skills and
# context; they just do not get the proactive layer.
SUPPORTED = ("claude", "codex", "gemini")

# Kept for the day one of these is verified: the matcher is written,
# but nothing ships until the agent is added to SUPPORTED above.
UNVERIFIED = ("cursor",)

# Where each agent expects its hook configuration, and whether that
# file holds other settings too. Codex reads .codex/hooks.json; gemini
# keeps hooks inside its settings file, so the config is merged in
# rather than overwriting whatever else is there.
CONFIG_LOCATION = {
    "claude": (".claude", "settings.json", True),
    "codex": (".codex", "hooks.json", False),
    "cursor": (".cursor", "hooks.json", False),
    "gemini": (".gemini", "settings.json", True),
}


# Gemini CLI names its lifecycle events differently, and shipping
# Claude's names to it produced a config the CLI loads and then ignores:
# three of the five events never matched anything, so the gate never
# ran, the nudges never ran, and the proactive layer was inert while
# looking installed. This mapping is Gemini's own, read out of
# packages/cli/src/commands/hooks/migrate.ts - what `gemini hooks
# migrate` applies to a Claude config.
#
# Stop and SessionEnd both land on AfterAgent: the end-of-session check
# has to be able to block, and Gemini's SessionEnd is advisory only.
GEMINI_EVENTS = {
    "UserPromptSubmit": "BeforeAgent",
    "PreToolUse": "BeforeTool",
    "PostToolUse": "AfterTool",
    "Stop": "AfterAgent",
    "SessionEnd": "AfterAgent",
}


def _rseng_root(agent: str) -> str:
    return f"{CONFIG_LOCATION[agent][0]}/rseng"


def hooks_config(agent: str, *, root: str | None = None) -> dict:
    """The hooks.json body for one agent."""
    if agent not in SUPPORTED:
        raise ValueError(f"{agent} has no known hook system")
    base = root or _rseng_root(agent)

    def run(script: str) -> dict:
        return {"type": "command", "command": f"python3 {base}/{script}"}

    config: dict = {
        "hooks": {
            "SessionStart": [{"hooks": [run("session_start.py")]}],
            "UserPromptSubmit": [{"hooks": [run("phase_status.py")]}],
            "PreToolUse": [
                {"matcher": WRITE_MATCHERS[agent], "hooks": [run("gate.py")]}
            ],
            "PostToolUse": [
                {"matcher": READ_MATCHERS[agent], "hooks": [run("signal_nudge.py")]}
            ],
        }
    }

    skill_tool = SKILL_MATCHERS.get(agent)
    if skill_tool:
        # Record every consultation, then surface the neighbours of the
        # skill just used.
        ledger = (
            'python3 -c "import json,sys;d=json.load(sys.stdin);'
            "s=(d.get('tool_input') or {}).get('skill');"
            "s and open('.rseng-agent-skills-usage.log','a').write(s+chr(10))\""
        )
        config["hooks"]["PreToolUse"].append(
            {"matcher": skill_tool, "hooks": [{"type": "command", "command": ledger}]}
        )
        config["hooks"]["PostToolUse"].append(
            {"matcher": skill_tool, "hooks": [run("related_nudge.py")]}
        )

    # Codex and gemini end a session with SessionEnd; claude with Stop.
    end_event = "SessionEnd" if agent in ("codex", "gemini") else "Stop"
    config["hooks"][end_event] = [{"hooks": [run("quality_check.py")]}]

    events = GEMINI_EVENTS if agent == "gemini" else {}
    if events:
        renamed: dict = {}
        for name, entries in config["hooks"].items():
            renamed.setdefault(events.get(name, name), []).extend(entries)
        config["hooks"] = renamed
    return config


def write_hook_scripts(repo_root: Path, rseng_dir: Path) -> list[Path]:
    """Copy the hook scripts and their data into one directory."""
    rseng_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name in HOOK_SCRIPTS:
        source = repo_root / "hooks" / name
        if not source.is_file():
            continue
        destination = rseng_dir / name
        destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        written.append(destination)
    return written


def write_hooks(repo_root: Path, agent: str, target_dir: Path) -> list[Path]:
    """Emit hooks.json and the scripts it runs, for one agent."""
    if agent not in SUPPORTED:
        return []
    directory, filename, shared = CONFIG_LOCATION[agent]
    config_dir = target_dir / directory
    written = write_hook_scripts(repo_root, config_dir / "rseng")
    hooks_file = config_dir / filename
    body = hooks_config(agent)
    if shared and hooks_file.is_file():
        # The file carries other settings; replace only the hooks key.
        try:
            existing = json.loads(hooks_file.read_text(encoding="utf-8"))
            if isinstance(existing, dict):
                existing["hooks"] = body["hooks"]
                body = existing
        except json.JSONDecodeError:
            pass
    hooks_file.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    written.append(hooks_file)
    return written
