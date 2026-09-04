"""Behaviour tests for the session hooks.

The hooks are the pack's enforcement layer and they run inside someone
else's coding session, which makes two failure modes expensive: a hook
that stops enforcing without saying so, and a hook that raises where the
user can see it. Both had happened. The gate matched Claude's four tool
names while being shipped to codex and gemini, so it allowed every write
on two of the three supported agents and left the stop-time audit
switched off with it; five hooks raised on payload shapes an agent host
can legitimately send.

Run with: uv run --directory pipeline pytest ../hooks/tests
"""

import json
import os
import pathlib
import subprocess
import sys

import pytest

HOOKS = pathlib.Path(__file__).resolve().parents[1]

# One per supported agent, as hook_wiring actually wires them up.
WRITE_TOOLS = [
    ("claude", "Write"),
    ("claude", "Edit"),
    ("claude", "MultiEdit"),
    ("claude", "NotebookEdit"),
    ("codex", "apply_patch"),
    ("codex", "shell"),
    ("gemini", "write_file"),
    ("gemini", "replace"),
]

MALFORMED = [
    '{"tool_name": "Write", "tool_input": "a bare string"}',
    '{"tool_name": 12345, "tool_input": 999}',
    '{"tool_input": {"skill": ["not", "a", "string"]}}',
    '{"tool_input": {"skill": 42}}',
    '{"tool_name": null}',
    '{"tool_input": null}',
    "not json at all",
    "",
    "[]",
    "null",
]


def run_hook(name, payload, cwd, env=None):
    return subprocess.run(
        [sys.executable, str(HOOKS / f"{name}.py")],
        input=payload,
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=30,
        env={**os.environ, **(env or {})},
        check=False,  # a non-zero exit is the behaviour under test
    )


@pytest.fixture
def project(tmp_path):
    """A project mid-session: some code, no practice artifacts yet."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print(1)\n")
    (tmp_path / ".rseng-agent-skills-coverage.md").write_text("")
    return tmp_path


@pytest.mark.parametrize("agent,tool", WRITE_TOOLS)
def test_gate_blocks_writes_for_every_supported_agent(project, agent, tool):
    """The regression that made the gate inert on codex and gemini.

    hook_wiring ships this gate to all three agents with their own tool
    names; matching Claude's literals meant two of them were never gated.
    """
    payload = json.dumps({"tool_name": tool, "tool_input": {"file_path": "a.py"}})
    assert run_hook("gate", payload, project).returncode == 2, (
        f"gate did not block a {agent} write via {tool}"
    )


def test_gate_allows_reads(project):
    payload = json.dumps({"tool_name": "Read", "tool_input": {"file_path": "a.py"}})
    assert run_hook("gate", payload, project).returncode == 0


@pytest.mark.parametrize("agent,tool", WRITE_TOOLS)
def test_every_agents_write_tool_is_classified_as_a_write(agent, tool):
    """The root cause, at the unit level.

    gate.py gates on this and phase_lib.record_write feeds the write
    counter that quality_check uses to decide whether the session wrote
    anything at all. A tool missing here silently switched off both the
    gate and the stop-time audit for that agent.
    """
    sys.path.insert(0, str(HOOKS))
    import tool_event

    assert tool_event.is_write(tool), f"{tool} ({agent}) not recognised as a write"


def test_a_non_string_tool_name_is_not_a_write():
    sys.path.insert(0, str(HOOKS))
    import tool_event

    for value in (12345, None, ["Write"], {"a": 1}):
        assert tool_event.is_write(value) is False


def test_gate_refuses_to_let_the_session_edit_its_own_records(project):
    for target in (
        ".claude/rseng/gate.py",
        ".codex/rseng/gate.py",
        ".gemini/rseng/phases.json",
        ".rseng-agent-skills-usage.log",
    ):
        payload = json.dumps(
            {"tool_name": "Write", "tool_input": {"file_path": target}}
        )
        assert run_hook("gate", payload, project).returncode == 2, target


def test_the_opt_out_does_not_unlock_the_hook_scripts(project):
    """The opt-out is one file the agent is allowed to create, so it must
    not also be the way to reach the enforcement code."""
    (project / ".rseng-agent-skills-relaxed").write_text("")
    payload = json.dumps(
        {"tool_name": "Write", "tool_input": {"file_path": ".claude/rseng/gate.py"}}
    )
    assert run_hook("gate", payload, project).returncode == 2


@pytest.mark.parametrize("payload", MALFORMED)
@pytest.mark.parametrize(
    "hook", ["gate", "quality_check", "related_nudge", "signal_nudge", "phase_status"]
)
def test_no_hook_shows_a_traceback_to_the_user(project, hook, payload):
    result = run_hook(hook, payload, project)
    assert "Traceback" not in result.stderr, f"{hook} raised on {payload!r}"


@pytest.mark.parametrize("hook", ["gate", "quality_check", "phase_status"])
def test_one_bad_byte_in_the_worklog_does_not_break_the_session(project, hook):
    """The worklog is agent-authored, so a stray byte is a matter of time.
    Decoding it strictly bricked every hook on every prompt thereafter."""
    (project / ".rseng-agent-skills-coverage.md").write_bytes(
        b"applied: rseng-testing \xff\xfe bad\n"
    )
    result = run_hook(hook, "{}", project)
    assert "Traceback" not in result.stderr


def test_a_dependencys_tests_do_not_satisfy_the_tests_requirement(project):
    """A virtualenv is not a test suite."""
    vendored = project / ".venv" / "lib" / "somelib" / "tests"
    vendored.mkdir(parents=True)
    (vendored / "test_dep.py").write_text("def test_x(): pass\n")
    (project / ".rseng-agent-skills-writes").write_text("w\n")
    result = run_hook("quality_check", "{}", project)
    assert "tests (at least" in result.stderr


def test_hooks_do_not_fail_on_a_read_only_project(project):
    """A hook must not raise because its own bookkeeping could not be
    written - that lands on the success path, after the agent complied."""
    (project / ".rseng-agent-skills-relaxed").write_text("")
    project.chmod(0o500)
    try:
        payload = json.dumps(
            {"tool_name": "Write", "tool_input": {"file_path": "a.py"}}
        )
        assert "Traceback" not in run_hook("gate", payload, project).stderr
    finally:
        project.chmod(0o700)
