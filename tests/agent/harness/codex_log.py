"""Codex writes no event stream; it writes a rollout log.

Ignoring it left codex sessions with no tokens, no cost and no
observable tool use, which the report then showed as zeros.
"""

from __future__ import annotations

import json
from pathlib import Path


def read_codex_rollout(sandbox: Path) -> dict | None:
    """Codex's own session log, from the isolated CODEX_HOME.

    Codex emits no stream on stdout but writes a complete rollout
    (token counts and every tool call) under
    <sandbox>/.agent-config/codex/sessions/. Ignoring it is what left
    codex sessions with no tokens, no cost and no observable tool use.
    """
    sessions = sandbox / ".agent-config" / "codex" / "sessions"
    if not sessions.is_dir():
        return None
    logs = sorted(sessions.rglob("rollout-*.jsonl"), key=lambda q: q.stat().st_mtime)
    if not logs:
        return None
    usage = None
    commands: list[str] = []
    messages = reasoning = 0
    model = effort = cli_version = None
    for line in logs[-1].read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        payload = event.get("payload") or {}
        # The model is in the turn_context header, not in any payload
        # that carries a "type". Only the typed events were read, so
        # every codex session was recorded with an empty model and the
        # report had nothing to show for which model produced it.
        if event.get("type") == "turn_context":
            model = payload.get("model") or model
            effort = payload.get("effort") or effort
        elif event.get("type") == "session_meta":
            cli_version = payload.get("cli_version") or cli_version
        kind = payload.get("type")
        if kind == "token_count":
            usage = (payload.get("info") or {}).get("total_token_usage") or usage
        elif kind == "custom_tool_call":
            commands.append(str(payload.get("input", ""))[:2000])
        elif kind == "message":
            messages += 1
        elif kind == "reasoning":
            reasoning += 1
    if usage is None and not commands and model is None:
        return None
    return {
        "model": model,
        "effort": effort,
        "cli_version": cli_version,
        "log": str(logs[-1]),
        "usage": usage or {},
        "tool_calls": len(commands),
        "commands": commands,
        "messages": messages,
        "reasoning_steps": reasoning,
    }
