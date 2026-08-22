"""The scenario catalogue, read from scenarios.yaml.

ONE NAME PER SCENARIO
---------------------
Scenarios used to carry a key and a separate `title`: the key `assess`
displayed as `repo-audit`, `analysis` as `data-analysis`, `minimal` as
`vague-novice-prompt`. Records were labelled with the key and the
report showed the title, so the same scenario appeared under two names
depending on where you looked. The key is now the name, and there is
no second one to keep in step with it.

The previous names still work on the command line - see ALIASES - so
`run.py assess` is not a broken command, it is the old spelling of
`run.py repo-audit`.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from harness import seeds

CATALOGUE_FILE = Path(__file__).resolve().parent.parent / "scenarios.yaml"


def load(path: Path | None = None) -> dict:
    return yaml.safe_load((path or CATALOGUE_FILE).read_text(encoding="utf-8"))


_RAW = load()

PROJECTS: dict = _RAW.get("projects") or {}
STANDALONE: dict = _RAW.get("standalone") or {}
LEVELS: dict = _RAW.get("levels") or {}

PROJECT_TASKS = {name: cfg["task"] for name, cfg in PROJECTS.items()}
# Both matrix projects and standalone scenarios can declare seed data;
# looking only at projects left every new standalone scenario with an
# empty sandbox and a prompt referring to files that were never written.
PROJECT_SEEDS = {
    name: cfg.get("seed_data")
    for name, cfg in list(PROJECTS.items()) + list(STANDALONE.items())
    if isinstance(cfg, dict)
}
PROMPT_LEVELS = {
    name: (cfg["prompt"] if isinstance(cfg, dict) else cfg)
    for name, cfg in LEVELS.items()
}
# Every prompt the suite sends is in scenarios.yaml rather than in the
# code that sends it, so the inputs of the experiment are reviewable
# in one file.
STANDALONE_PROMPTS = {
    name: cfg["prompt"]
    for name, cfg in STANDALONE.items()
    if isinstance(cfg, dict) and cfg.get("prompt")
}

DEFAULT_CELLS = _RAW.get("default_cells", "")
ALL_CELLS = ",".join(f"{p}:{lv}" for p in PROJECT_TASKS for lv in PROMPT_LEVELS)

# Old spellings, so existing commands and saved records still resolve.
ALIASES = {
    "analysis": "data-analysis",
    "tool": "growth-fitting",
    "pipeline": "sensor-pipeline",
    "mltrain": "ml-classifier",
    "hpcsim": "hpc-simulation",
    "sensitive": "sensitive-qc",
    "assess": "repo-audit",
    "check": "repo-audit",
    "novice": "novice-request",
    "deps": "dependency-lifecycle",
    "develop": "package-build",
    "minimal": "vague-novice-prompt",
    "moderate": "clear-brief",
    "full": "publication-ready-brief",
}


def canonical(name: str) -> str:
    """The current name for a scenario, project or level."""
    return ALIASES.get(name, name)


def matrix_prompt(project: str, level: str) -> str:
    project, level = canonical(project), canonical(level)
    task = PROJECT_TASKS[project]
    lowered = task[0].lower() + task[1:]
    return PROMPT_LEVELS[level].format(task=task, task_lc=lowered)


# --- seed data -------------------------------------------------------
# The generators live in harness/seeds.py; a scenario names one by key.
SEED_GENERATORS = seeds.GENERATORS


def seed(sandbox: Path, project: str) -> str | None:
    """Seed the sandbox for a project; returns the seed used, if any."""
    name = PROJECT_SEEDS.get(canonical(project))
    generator = SEED_GENERATORS.get(name)
    if generator is None:
        return None
    generator(sandbox)
    return name
