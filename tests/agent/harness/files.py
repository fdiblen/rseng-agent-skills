"""Reading what a session left in its sandbox.

The delivered tree is a DIFF against a snapshot taken before the agent
started, not a listing: a plain listing counted the scenario seed and
the harness\'s own pack install as the agent\'s output.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

from harness.config import PRE_RUN


def _file_state(root: Path) -> dict:
    """Relative path -> (size, mtime_ns) for every file under root."""
    state = {}
    if not root.is_dir():
        return state
    for q in root.rglob("*"):
        try:
            if not q.is_file():
                continue
            info = q.stat()
            state["/".join(q.relative_to(root).parts)] = (
                info.st_size,
                info.st_mtime_ns,
            )
        except OSError:
            continue
    return state


# Directory names that never hold code the agent wrote.
VENDOR_DIRS = frozenset(
    {
        "node_modules",
        "site-packages",
        "__pycache__",
        "vendor",
        "dist-info",
        "egg-info",
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".nox",
        "build",
        "_build",
    }
)

# Agent working directories, per target.
AGENT_DIRS = frozenset(
    {
        ".agent-config",
        ".claude",
        ".agents",
        ".cursor",
        ".codex",
        ".gemini",
    }
)


def venv_roots(sandbox: Path) -> set[Path]:
    """Every virtualenv inside the sandbox, found structurally.

    A virtualenv is identified by its pyvenv.cfg, not by being called
    ".venv". A baseline session created one called plain `venv`, which
    every name-based filter here missed: the census counted 4,026 files
    and 1.7M lines for a project whose agent wrote ONE file, and the
    check registry scored 8,051 source files of which 8,050 were
    third-party library code. Names are a guess; the marker file is
    what a virtualenv actually is.
    """
    found = set()
    try:
        for marker in sandbox.rglob("pyvenv.cfg"):
            found.add(marker.parent)
    except OSError:
        pass
    return found


def is_agent_output(path: Path, sandbox: Path, venvs: set[Path] | None = None) -> bool:
    """Did the agent write this, or did a tool put it there?"""
    try:
        parts = path.relative_to(sandbox).parts
    except ValueError:
        return False
    if any(
        part.startswith(".") or part in VENDOR_DIRS or part in AGENT_DIRS
        for part in parts
    ):
        return False
    roots = venv_roots(sandbox) if venvs is None else venvs
    return not any(root == path or root in path.parents for root in roots)


NOT_DELIVERED = (
    ".agent-config",
    ".claude",
    ".agents",
    ".cursor",
    ".codex",
    ".gemini",
    ".venv",
    ".test-venv",
    "__pycache__",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".coverage",
    ".rseng-tokens.json",
    "node_modules",
    "site-packages",
)


def project_sources(sandbox: Path) -> list[Path]:
    """The agent's own Python files - no venvs, caches or agent dirs."""
    venvs = venv_roots(sandbox)
    return [q for q in sandbox.rglob("*.py") if is_agent_output(q, sandbox, venvs)]


def project_tree(sandbox: Path, limit: int = 200) -> list[str] | None:
    """Relative paths of the files the agent actually delivered.

    A file counts as delivered if it was not there before the session,
    or if the session changed it. Everything the harness put in place -
    the scenario seed and the installed pack - is excluded by
    comparison against the pre-run snapshot rather than by a hardcoded
    name list that would go stale as the installers change.
    """
    if sandbox is None or not sandbox.is_dir():
        return None
    before = dict(PRE_RUN)
    found = []
    # The same structural rule the census and the registry use. This
    # loop kept its own name list and so listed a virtualenv called
    # `venv` as files the agent delivered.
    venvs = venv_roots(sandbox)
    for path, state in sorted(_file_state(sandbox).items()):
        if path.endswith(".pyc") or not is_agent_output(sandbox / path, sandbox, venvs):
            continue
        if before.get(path) == state:
            continue  # untouched seed or pack file
        found.append(path)
        if len(found) >= limit:
            break
    return found


SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][A-Za-z0-9+/_-]{16,}"
)


def code_census(sandbox: Path) -> dict:
    """Size/lint/complexity census of the generated code, recorded
    into the session analytics before the sandbox is cleaned."""

    files = loc = defs = branches = tests = 0
    max_depth = 0
    # Same rule as project_sources. This loop had its own weaker
    # filter - dot-prefixed parts only - so a virtualenv named `venv`
    # was counted as the agent's code.
    venvs = venv_roots(sandbox)
    for q in sandbox.rglob("*.py"):
        if not is_agent_output(q, sandbox, venvs):
            continue
        try:
            src = q.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(src)
        except (OSError, SyntaxError):
            continue
        files += 1
        loc += sum(1 for line in src.splitlines() if line.strip())
        if q.name.startswith("test_") or q.name.endswith("_test.py"):
            tests += 1

        def depth(node, d=0):
            nonlocal max_depth
            max_depth = max(max_depth, d)
            for child in ast.iter_child_nodes(node):
                extra = isinstance(
                    child,
                    (ast.If, ast.For, ast.While, ast.Try, ast.With),
                )
                depth(child, d + (1 if extra else 0))

        depth(tree)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defs += 1
            if isinstance(node, (ast.If, ast.For, ast.While, ast.BoolOp)):
                branches += 1
    # ruff exits 1 both for "found problems" and for "could not run"
    # (no such module). Only a JSON payload proves it actually linted,
    # so an absent ruff records None - never a clean 0.
    lint = None
    try:
        run = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "--isolated",
                "--output-format",
                "json",
                ".",
            ],
            cwd=sandbox,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if run.returncode in (0, 1) and run.stdout.strip():
            lint = len(json.loads(run.stdout))
        elif run.returncode == 0:
            lint = 0
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        lint = None
    return {
        "py_files": files,
        "loc": loc,
        "functions": defs,
        "test_files": tests,
        # Branch-point count (if/for/while/boolop), a size proxy - NOT
        # McCabe cyclomatic complexity, which is per-function and adds
        # comprehensions and handlers.
        "branch_points": branches,
        "max_nesting": max_depth,
        "lint_findings": lint,
    }


def sandbox_text(sandbox: Path) -> str:
    chunks = []
    for path in sandbox.rglob("*"):
        if (
            path.is_file()
            and ".claude" not in path.parts
            and path.stat().st_size < 200_000
        ):
            try:
                chunks.append(path.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, OSError):
                continue
    return "\n".join(chunks)
