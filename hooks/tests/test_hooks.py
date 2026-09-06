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
import shutil
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


SHELL_WRITES = [
    ("cat > app.py <<EOF", True),
    ("echo x >> log.txt", True),
    ("rm .rseng-agent-skills-writes", True),
    ("mkdir -p src", True),
    ("sed -i s/a/b/ f.py", True),
    ("ls && rm -rf build", True),
    ("sudo mkdir /opt/x", True),
    ("git add -A", True),
    ("git apply p.patch", True),
    ("ls -la", False),
    ("grep -rn foo . | head", False),
    ("cat README.md", False),
    ("echo hi 2>&1", False),
    ("sed s/a/b/ f.py", False),
    ("git status --porcelain", False),
    ("git log --oneline", False),
    ("git rev-parse HEAD", False),
    ("pytest -q", False),
]


@pytest.mark.parametrize("command,is_write", SHELL_WRITES)
def test_a_shell_command_is_judged_by_what_it_does(command, is_write):
    """A shell is a write tool only sometimes, and the tool name cannot
    tell `git status` from `rm -rf`. Claude's Bash was in no write list at
    all, so `cat > app.py <<EOF` was never gated, never counted as a
    write, and left the stop-time audit believing nothing was written."""
    sys.path.insert(0, str(HOOKS))
    import tool_event

    assert tool_event.shell_writes(command) is is_write, command


@pytest.mark.parametrize("tool", ["Bash", "shell", "run_shell_command"])
def test_the_gate_holds_a_write_made_through_a_shell(project, tool):
    payload = json.dumps(
        {"tool_name": tool, "tool_input": {"command": "cat > app.py <<EOF"}}
    )
    assert run_hook("gate", payload, project).returncode == 2


@pytest.mark.parametrize("tool", ["Bash", "shell"])
def test_the_gate_lets_a_shell_read_through(project, tool):
    payload = json.dumps({"tool_name": tool, "tool_input": {"command": "ls -la"}})
    assert run_hook("gate", payload, project).returncode == 0


def test_one_allowed_path_does_not_shield_the_rest_of_a_command(project):
    """The gate inspected targets[0] only, so naming the worklog first
    carried anything else in the same command past it."""
    payload = json.dumps(
        {
            "tool_name": "shell",
            "tool_input": {"command": "touch .rseng-agent-skills-coverage.md evil.py"},
        }
    )
    assert run_hook("gate", payload, project).returncode == 2


def test_the_worklog_alone_still_passes(project):
    payload = json.dumps(
        {
            "tool_name": "Write",
            "tool_input": {"file_path": ".rseng-agent-skills-coverage.md"},
        }
    )
    assert run_hook("gate", payload, project).returncode == 0


def test_unreadable_phase_data_holds_the_write_instead_of_allowing_it(
    project, tmp_path
):
    """Fail closed. An unhandled JSONDecodeError exits 1, and a PreToolUse
    hook exiting 1 is a warning - the write proceeds. So corrupting one
    JSON file was a way to switch the gate off from inside the project."""
    copy = tmp_path / "hooks"
    shutil.copytree(HOOKS, copy)
    (copy / "phases.json").write_text("NOT JSON{")
    payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": "a.py"}})
    result = subprocess.run(
        [sys.executable, str(copy / "gate.py")],
        input=payload,
        capture_output=True,
        text=True,
        cwd=project,
        timeout=30,
        check=False,
    )
    assert result.returncode == 2
    assert "Traceback" not in result.stderr
    assert "unreadable" in result.stderr


def test_the_session_cannot_create_its_own_opt_out(project):
    """The cheapest way to satisfy a gate is to delete the gate.

    The opt-out was a normal file the agent could write, so one Write of
    .rseng-agent-skills-relaxed switched off the phases, the ledger and the
    stop-time audit for the rest of the session - without touching anything
    the tamper check protects. It belongs to the user, not to the session.
    """
    payload = json.dumps(
        {
            "tool_name": "Write",
            "tool_input": {"file_path": ".rseng-agent-skills-relaxed"},
        }
    )
    result = run_hook("gate", payload, project)
    assert result.returncode == 2
    assert "the user's to create" in result.stderr


def test_a_user_created_opt_out_still_relaxes_the_gate(project):
    """Refusing to let the agent create it must not break the opt-out."""
    (project / ".rseng-agent-skills-relaxed").write_text("")
    payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": "a.py"}})
    assert run_hook("gate", payload, project).returncode == 0


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


def test_reading_a_skill_counts_as_consulting_it(project):
    """Only claude and cursor have a Skill tool to hook, so on codex,
    gemini, copilot and antigravity the ledger stayed empty forever - and
    the gate hard-requires a non-empty ledger. Every write was refused for
    the rest of the session, with a message telling the agent to use a
    tool it does not have. Reading the file is the consultation there."""
    skill = project / ".agents" / "skills" / "rseng-testing"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# rseng-testing\n")

    payload = json.dumps(
        {
            "tool_name": "read_file",
            "tool_input": {"file_path": ".agents/skills/rseng-testing/SKILL.md"},
        }
    )
    run_hook("signal_nudge", payload, project)
    ledger = (project / ".rseng-agent-skills-usage.log").read_text()
    assert "rseng-testing" in ledger


def test_a_skill_read_through_a_shell_counts_too(project):
    skill = project / ".agents" / "skills" / "rseng-honesty"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# rseng-honesty\n")
    payload = json.dumps(
        {
            "tool_name": "shell",
            "tool_input": {"command": "cat .agents/skills/rseng-honesty/SKILL.md"},
        }
    )
    run_hook("signal_nudge", payload, project)
    assert "rseng-honesty" in (project / ".rseng-agent-skills-usage.log").read_text()


def test_the_ledger_does_not_grow_a_duplicate_on_every_read(project):
    skill = project / ".agents" / "skills" / "rseng-testing"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# rseng-testing\n")
    payload = json.dumps(
        {
            "tool_name": "read_file",
            "tool_input": {"file_path": ".agents/skills/rseng-testing/SKILL.md"},
        }
    )
    for _ in range(3):
        run_hook("signal_nudge", payload, project)
    lines = (project / ".rseng-agent-skills-usage.log").read_text().split()
    assert lines.count("rseng-testing") == 1


def test_an_ordinary_file_read_writes_no_ledger_entry(project):
    payload = json.dumps(
        {"tool_name": "read_file", "tool_input": {"file_path": "src/app.py"}}
    )
    run_hook("signal_nudge", payload, project)
    ledger = project / ".rseng-agent-skills-usage.log"
    assert not ledger.is_file() or "rseng-" not in ledger.read_text()
