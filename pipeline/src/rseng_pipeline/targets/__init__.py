"""Adapter target registrations.

Each module in this package defines one agent target and registers it via
the @target decorator; importing the package registers them all.
"""

from . import codex, copilot, cursor, gemini  # noqa: F401
