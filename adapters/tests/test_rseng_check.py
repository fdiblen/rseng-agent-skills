"""Behaviour tests for the self-check shipped to the hookless agents.

Codex, Gemini, Antigravity, Copilot and Cursor have no hook system, so
this script is the whole enforcement layer on those platforms - and it
had no tests. The failure that motivated these: with its two data files
absent it skipped the skill inventory, every cluster check and all 52
relevance rules, and then printed "practice artifacts and phased
coverage complete". A checker that cannot run must not report a pass.

The build_adapters copy is exercised, not the source in adapters/: the
source deliberately has no data files beside it, and what users get is
what matters.

Run with: uv run --directory pipeline pytest ../adapters/tests
"""

import pathlib
import shutil
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SHIPPED = REPO / "dist" / "codex" / "rseng-check"


def run(script, root):
    return subprocess.run(
        [sys.executable, str(script), str(root)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,  # a non-zero exit is the behaviour under test
    )


@pytest.fixture
def complete(tmp_path):
    """The check as an installed project actually receives it."""
    dest = tmp_path / "check"
    shutil.copytree(SHIPPED, dest)
    return dest / "rseng_check.py"


@pytest.fixture
def project(tmp_path):
    """A project with code and none of the practice artifacts."""
    root = tmp_path / "proj"
    (root / "src").mkdir(parents=True)
    (root / "src" / "app.py").write_text("print(1)\n")
    return root


def test_a_check_that_cannot_run_does_not_report_success(tmp_path, project):
    """Fail closed. This printed 'complete' on any project whatsoever."""
    lone = tmp_path / "lone"
    lone.mkdir()
    shutil.copy(SHIPPED / "rseng_check.py", lone)

    result = run(lone / "rseng_check.py", project)
    assert result.returncode == 2
    assert "cannot run" in result.stdout
    assert "phased coverage complete" not in result.stdout


@pytest.mark.parametrize("missing", ["phases.json", "signals.json"])
def test_either_data_file_alone_is_enough_to_refuse(complete, project, missing):
    (complete.parent / missing).unlink()
    result = run(complete, project)
    assert result.returncode == 2
    assert missing in result.stdout


def test_the_shipped_copy_carries_its_data_files(complete):
    names = {p.name for p in complete.parent.iterdir()}
    assert {"phases.json", "signals.json"} <= names


def test_every_target_ships_a_runnable_check():
    """The data files are copied per target, so a new adapter can forget
    them - and before the fail-closed guard that silently became a pass."""
    for script in sorted((REPO / "dist").rglob("rseng_check.py")):
        beside = {p.name for p in script.parent.iterdir()}
        assert {"phases.json", "signals.json"} <= beside, script


def test_a_bare_project_fails_the_artifact_floor(complete, project):
    result = run(complete, project)
    assert result.returncode == 1
    assert "missing practice artifacts" in result.stdout
    for expected in ("README", "LICENSE", "CITATION.cff", "tests"):
        assert expected in result.stdout


def test_a_project_with_no_code_is_not_audited(complete, tmp_path):
    empty = tmp_path / "docs-only"
    empty.mkdir()
    (empty / "notes.md").write_text("nothing to compile\n")
    result = run(complete, empty)
    assert result.returncode == 0
    assert "nothing to audit" in result.stdout


def test_a_waiver_needs_a_reason(complete, project):
    (project / ".rseng-check-waivers").write_text(
        "LICENSE\nREADME: docs live elsewhere\n"
    )
    out = run(complete, project).stdout
    assert "README" not in out  # waived with a reason
    assert "LICENSE" in out  # no reason given, so not waived


def test_more_than_one_path_is_refused(complete, project):
    result = subprocess.run(
        [sys.executable, str(complete), str(project), str(project)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 2


def test_a_missing_directory_is_refused(complete, tmp_path):
    result = run(complete, tmp_path / "does-not-exist")
    assert result.returncode == 2
    assert "not a directory" in result.stdout


ENV_DECLARATIONS = [
    ("pyproject.toml", "[project]\nname = 'demo'\n"),
    ("package.json", '{"name": "demo"}\n'),
    ("DESCRIPTION", "Package: demo\n"),
    ("renv.lock", "{}\n"),
    ("Project.toml", 'name = "Demo"\n'),
    ("CMakeLists.txt", "project(demo)\n"),
    ("meson.build", "project('demo')\n"),
    ("conanfile.txt", "[requires]\n"),
    ("vcpkg.json", '{"name": "demo"}\n'),
]


@pytest.mark.parametrize("name,body", ENV_DECLARATIONS)
def test_every_ecosystems_environment_declaration_is_accepted(
    complete, project, name, body
):
    """The check accepted only Python's four, so a JS, R, Julia or C
    project was told it had no dependency declaration and had no way to
    satisfy the demand."""
    (project / name).write_text(body)
    assert "environment/dependency declaration" not in run(complete, project).stdout


def test_a_project_declaring_nothing_is_still_asked_for_a_declaration(
    complete, project
):
    assert "environment/dependency declaration" in run(complete, project).stdout


def test_the_check_and_the_hooks_accept_the_same_declarations():
    """Two copies of this list exist because the self-check ships alone
    and cannot import the hooks. They have drifted before."""
    import importlib.util

    sys.path.insert(0, str(REPO / "hooks"))
    import phase_lib

    spec = importlib.util.spec_from_file_location(
        "shipped_check", SHIPPED / "rseng_check.py"
    )
    shipped = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(shipped)

    assert shipped.ENV_DECLARATIONS == phase_lib.ENV_DECLARATIONS
