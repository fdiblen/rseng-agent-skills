"""SessionStart hook: hand the pack's standing brief to the agent.

This was a bare `cat` of session-context.md. Gemini CLI parses a hook's
stdout as JSON and treats anything else as a system message, so the brief
never reached the model's context there - the one hook whose entire job
is putting it there.
"""

import pathlib
import sys

import phase_lib

phase_lib.record_hook("session_start")
brief = pathlib.Path(__file__).parent / "session-context.md"
if not brief.is_file():
    sys.exit(0)
phase_lib.emit_context(
    "SessionStart", brief.read_text(encoding="utf-8", errors="replace")
)
sys.exit(0)
