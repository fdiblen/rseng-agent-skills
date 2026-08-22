"""Starting contents for each scenario's sandbox.

Deterministic: the same files for every arm and every run, so a
difference between arms can never come from different inputs.

Each seed sets up a situation a research group actually arrives in - a
notebook that only runs in the author's cell order, code inherited from
someone who left, a file that has outgrown memory - rather than a blank
directory. A scenario can only exercise a skill if the sandbox gives
that skill something to be needed for.
"""

from __future__ import annotations

import json
import math
import random
import textwrap
from pathlib import Path


def _readings(sandbox: Path, n: int, name: str = "readings.csv") -> None:
    """A signal with a slow oscillation, noise and periodic spikes."""
    rng = random.Random(7)
    rows = ["time,signal"]
    for i in range(n):
        x = i * 0.1
        base = 2.0 + math.sin(x / 3)
        spike = 3.0 if i % 97 == 0 else 0.0
        rows.append(f"{x:.2f},{base + spike + rng.gauss(0, 0.05):.4f}")
    (sandbox / name).write_text("\n".join(rows) + "\n", encoding="utf-8")


def _write(sandbox: Path, name: str, body: str) -> None:
    path = sandbox / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(body).lstrip("\n"), encoding="utf-8")


def seed_peaks(sandbox: Path) -> None:
    """measurements.csv - three Gaussian peaks on a noisy baseline."""
    rng = random.Random(42)
    rows = ["time,signal"]
    for i in range(500):
        x = i * 0.1
        signal = 1.0 + 0.05 * rng.gauss(0, 1)
        for center, height, width in ((12, 4.0, 0.8), (25, 2.5, 1.2), (38, 3.2, 0.6)):
            signal += height * math.exp(-((x - center) ** 2) / (2 * width**2))
        rows.append(f"{x:.2f},{signal:.4f}")
    (sandbox / "measurements.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")


def seed_classifier(sandbox: Path) -> None:
    """sensor_readings.csv - imbalanced fault labels, ~12% positive."""
    rng = random.Random(11)
    rows = ["temp_c,vibration_hz,current_a,age_days,faulty"]
    for _ in range(600):
        faulty = 1 if rng.random() < 0.12 else 0
        temp = rng.gauss(45 + 18 * faulty, 6)
        vibration = abs(rng.gauss(120 + 90 * faulty, 30))
        current = abs(rng.gauss(2.1 + 0.9 * faulty, 0.4))
        age = rng.randint(10, 1500)
        rows.append(f"{temp:.2f},{vibration:.1f},{current:.3f},{age},{faulty}")
    (sandbox / "sensor_readings.csv").write_text(
        "\n".join(rows) + "\n", encoding="utf-8"
    )


def seed_survey(sandbox: Path) -> None:
    """survey_participants.csv - quasi-identifiers, small districts."""
    rng = random.Random(23)
    districts = ["AB1", "AB2", "CD3", "CD4", "EF5", "EF6", "GH7"]
    rows = ["participant_id,year_of_birth,postcode_district,q1,q2,q3"]
    for i in range(180):
        answers = ",".join(str(rng.randint(1, 5)) for _ in range(3))
        rows.append(
            f"P{1000 + i},{rng.randint(1938, 2006)},{rng.choice(districts)},{answers}"
        )
    (sandbox / "survey_participants.csv").write_text(
        "\n".join(rows) + "\n", encoding="utf-8"
    )


def seed_notebook(sandbox: Path) -> None:
    """analysis.ipynb - correct only in the author's cell order.

    The helper is defined in a cell BELOW its first use, so a clean
    top-to-bottom run raises NameError. That is the hidden-state
    problem notebooks are known for, and it is what makes the file
    unshareable rather than merely untidy.
    """
    cells = [
        (
            "code",
            (
                "import csv, statistics\n"
                "rows = list(csv.reader(open('readings.csv')))\n"
                "header, rows = rows[0], rows[1:]\n"
            ),
        ),
        ("markdown", "# Signal analysis\n\nQuick look before the group meeting.\n"),
        ("code", "vals = [float(r[1]) for r in rows]\nWINDOW = 5\n"),
        (
            "code",
            (
                "def smooth(xs, w):\n"
                "    return [statistics.mean(xs[max(0, i - w):i + 1])"
                " for i in range(len(xs))]\n"
            ),
        ),
        (
            "code",
            (
                "sm = smooth(vals, WINDOW)\n"
                "peaks = [i for i in range(1, len(sm) - 1)"
                " if sm[i] > sm[i - 1] and sm[i] > sm[i + 1]]\n"
                "print(len(peaks), 'peaks')\n"
            ),
        ),
    ]
    notebook = {
        "cells": [
            {
                "cell_type": kind,
                "metadata": {},
                "source": source.splitlines(keepends=True),
                **({"outputs": [], "execution_count": n} if kind == "code" else {}),
            }
            for n, (kind, source) in enumerate(cells, start=1)
        ],
        "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    (sandbox / "analysis.ipynb").write_text(
        json.dumps(notebook, indent=1), encoding="utf-8"
    )
    _readings(sandbox, 400)


def seed_slow(sandbox: Path) -> None:
    """A quadratic hot loop that has a linear equivalent.

    Correct but O(n^2), so the fix is a genuine algorithmic one and the
    answer can be checked: the mean pairwise distance must not change.
    """
    _write(
        sandbox,
        "slow_analysis.py",
        '''
        """Pairwise similarity over instrument readings."""
        import csv


        def load(path):
            with open(path, newline="") as handle:
                reader = csv.reader(handle)
                next(reader)
                return [float(row[1]) for row in reader]


        def mean_pairwise_distance(values):
            total = 0.0
            count = 0
            for i in range(len(values)):
                for j in range(len(values)):
                    if i != j:
                        total += abs(values[i] - values[j])
                        count += 1
            return total / count


        if __name__ == "__main__":
            data = load("readings.csv")
            print(f"mean pairwise distance: {mean_pairwise_distance(data):.6f}")
        ''',
    )
    _readings(sandbox, 3000)


def seed_legacy(sandbox: Path) -> None:
    """Inherited code: no tests, no docs, bare excepts, magic numbers.

    The window length the prompt asks to change is the literal 7, and
    it is not named anywhere - so changing it safely needs a
    characterization test first.
    """
    _write(
        sandbox,
        "figure3.py",
        """
        import csv, math

        def go(f):
            d=[]
            for r in csv.reader(open(f)):
                try: d.append(float(r[1]))
                except: pass
            o=[]
            for i in range(len(d)):
                s=0; c=0
                for j in range(i-7, i+1):
                    if j>=0: s+=d[j]; c+=1
                o.append(s/c)
            m=sum(o)/len(o)
            v=math.sqrt(sum((x-m)**2 for x in o)/len(o))
            t=[i for i,x in enumerate(o) if x>m+2*v]
            print(len(t))
            return o,t

        if __name__=="__main__":
            go("readings.csv")
        """,
    )
    _readings(sandbox, 500)


def seed_releasable(sandbox: Path) -> None:
    """Sound code with nothing that makes it findable or citable.

    Tests pass and the API is documented; what is missing is the
    release apparatus - version tagging, licence, citation metadata,
    changelog, archiving.
    """
    _write(
        sandbox,
        "src/peakfit/__init__.py",
        '''
        """Peak fitting for 1-D signals."""

        __version__ = "0.4.0"
        ''',
    )
    _write(
        sandbox,
        "src/peakfit/core.py",
        '''
        """Find local maxima in a 1-D signal."""


        def find_peaks(values, threshold=0.0):
            """Return indices of strict local maxima above `threshold`."""
            return [
                i
                for i in range(1, len(values) - 1)
                if values[i] > values[i - 1]
                and values[i] > values[i + 1]
                and values[i] > threshold
            ]
        ''',
    )
    _write(
        sandbox,
        "tests/test_core.py",
        """
        from peakfit.core import find_peaks


        def test_finds_a_single_peak():
            assert find_peaks([0, 1, 0]) == [1]


        def test_threshold_excludes_small_peaks():
            assert find_peaks([0, 1, 0], threshold=2) == []
        """,
    )
    _write(
        sandbox,
        "pyproject.toml",
        """
        [build-system]
        requires = ["setuptools>=61"]
        build-backend = "setuptools.build_meta"

        [project]
        name = "peakfit"
        version = "0.4.0"
        description = "Peak fitting for 1-D signals"
        requires-python = ">=3.9"
        """,
    )
    _write(
        sandbox,
        "README.md",
        """
        # peakfit

        Finds peaks in 1-D signals.

        ```python
        from peakfit.core import find_peaks
        ```
        """,
    )


def seed_internal(sandbox: Path) -> None:
    """An in-house tool with no route in for an outside contributor.

    Hardcoded fileserver path, a named gatekeeper, no licence, no
    contributing guide, no issue template.
    """
    _write(
        sandbox,
        "labtools.py",
        '''
        """Group tool for batch-converting instrument exports."""
        import csv
        import os

        # Set for our group's fileserver.
        DATA_ROOT = "/mnt/groupshare/instruments"
        CONTACT = "j.smith@institute.example"


        def convert(run_id):
            """Convert one instrument run to CSV."""
            source = os.path.join(DATA_ROOT, run_id, "raw.txt")
            with open(source) as handle:
                rows = [line.split() for line in handle if not line.startswith("#")]
            out = os.path.join(DATA_ROOT, run_id, "converted.csv")
            with open(out, "w", newline="") as handle:
                csv.writer(handle).writerows(rows)
            return out
        ''',
    )
    _write(
        sandbox,
        "README.md",
        """
        # labtools

        Internal converter for the group's instrument exports.
        Ask Jane before changing it.
        """,
    )


def seed_bigdata(sandbox: Path) -> None:
    """A whole-file load, against a file that will not fit next time."""
    _write(
        sandbox,
        "summarise.py",
        '''
        """Summarise instrument readings."""
        import csv


        def summarise(path):
            with open(path, newline="") as handle:
                reader = csv.reader(handle)
                next(reader)
                # The whole file, in memory, all at once.
                rows = [(row[0], float(row[1])) for row in reader]
            values = [value for _, value in rows]
            return {
                "n": len(values),
                "mean": sum(values) / len(values),
                "max": max(values),
                "min": min(values),
            }


        if __name__ == "__main__":
            print(summarise("readings.csv"))
        ''',
    )
    _readings(sandbox, 5000)


GENERATORS = {
    "peaks": seed_peaks,
    "classifier": seed_classifier,
    "survey": seed_survey,
    "notebook": seed_notebook,
    "slow": seed_slow,
    "legacy": seed_legacy,
    "releasable": seed_releasable,
    "internal": seed_internal,
    "bigdata": seed_bigdata,
}
