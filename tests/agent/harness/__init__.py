"""Pieces of the agent test harness, importable on their own.

run.py grew to a single 3,000-line module holding sandbox setup, agent
launching, telemetry parsing, scoring and the CLI. Splitting it lets
each part be tested and reused without starting a live session.
"""
