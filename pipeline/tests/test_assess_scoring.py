"""The assessment instrument must be able to tell two audits apart.

The version this replaces asked yes/no questions with thresholds set
below what either arm produced. On a real run, 19 of 23 comparisons
came back "both arms pass", and the only two checks that moved were
the crudest: whether the text contained "http", and a keyword match on
"priorit". Breadth was measured as 14/14 against 12/14 and then thrown
away by a threshold of 8 that both cleared.
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tests" / "agent"))

from harness import assess

THOROUGH = """
# Repository assessment

1. **Licensing (critical)** - there is no LICENSE file. Add an
   OSI-approved licence; SPDX identifiers make it machine readable.
2. **Testing** - no pytest suite exists. Add tests/test_analyze.py.
3. **Documentation** - no README. Document install and usage.
4. **Citation** - add a CITATION.cff in Citation File Format so the
   work is citable; mint a DOI with Zenodo.
5. **Reproducible environment** - no pyproject.toml and no lockfile;
   dependencies are undeclared.
6. **Version control** - no .gitignore, so caches get committed.
7. **Continuous integration** - no GitHub Actions workflow runs tests.
8. **Security** - no scan for hardcoded credentials.
9. **Data management** - the dataset has no provenance record.
10. **AI declaration** - add aidecl.yaml recording AI involvement.
11. **Packaging** - the code is a flat script, not an installable module.
12. **Code quality** - no lint configuration, no type hints.
13. **FAIR** - the software does not meet FAIR4RS: not findable or reusable.
14. **Contributing** - no CONTRIBUTING guide or code of conduct.

Start with the licence and the README: they block reuse entirely.
"""

SHALLOW = """
The repository contains a single analysis script. There is no licence
file, no readme, and no test suite. The code works but should be
tidied up and documented before anyone else uses it.
"""


def test_breadth_is_kept_as_a_ratio_not_a_threshold():
    thorough = assess.measure(THOROUGH)
    shallow = assess.measure(SHALLOW)
    assert thorough["breadth"] > shallow["breadth"]
    # The old instrument collapsed both of these to "pass" at 8 areas.
    assert thorough["areas_covered"] != shallow["areas_covered"]
    assert 0.0 <= shallow["breadth"] <= 1.0


def test_the_instrument_separates_a_thorough_audit_from_a_shallow_one():
    """Per-area checks give fourteen chances to differ, not one."""

    def run(text):
        outcomes = []
        assess.emit_checks(
            text,
            "probe",
            lambda ok, label: outcomes.append((bool(ok), label)),
            lambda _msg: None,
        )
        return outcomes

    thorough = run(THOROUGH)
    shallow = run(SHALLOW)
    assert len(thorough) == len(shallow), "same battery for both"

    differing = sum(
        1 for (a, _), (b, _) in zip(thorough, shallow, strict=True) if a != b
    )
    # The old battery moved on 2 of 11 checks between real arms.
    assert differing >= 8, (
        f"only {differing} of {len(thorough)} checks discriminate - "
        "the instrument is saturated again"
    )

    passed_thorough = sum(1 for ok, _ in thorough if ok)
    passed_shallow = sum(1 for ok, _ in shallow if ok)
    assert passed_thorough > passed_shallow


def test_a_named_standard_is_not_satisfied_by_any_stray_url():
    """The old check was `"http" in text`, which a link in a footer met."""
    assert assess.measure("see https://example.com/blog")["standard_count"] == 0
    assert assess.measure("follows the FAIR4RS principles")["standard_count"] >= 1


def test_naming_concrete_artifacts_beats_vague_advice():
    vague = assess.measure("you should improve the documentation and testing")
    concrete = assess.measure("add LICENSE, CITATION.cff and pyproject.toml")
    assert vague["artifact_count"] < concrete["artifact_count"]


def test_ordering_is_detected_from_a_numbered_list_too():
    assert assess.measure("1. add a licence\n2. write tests\n")["prioritised"]
    assert assess.measure("the priority is the licence")["prioritised"]
    assert not assess.measure("the repo has no licence and no tests")["prioritised"]


def test_licence_is_matched_by_stem_not_by_dialect():
    """British and American spellings are the same finding.

    The scenario check required the exact substring "license", so a
    baseline audit that wrote "licence" and "licensing" throughout was
    recorded as having failed to flag the missing licence. Worse, the
    two arms can differ in dialect, which makes a spelling difference
    look like a quality difference.
    """
    british = "There is no LICENCE file; licensing is undefined."
    american = "There is no LICENSE file; licensing is undefined."
    for text in (british, american):
        assert "licensing" in text.lower()
        assert any(s in text.lower() for s in ("licen",)), text
    # The graded battery already used the stem, and must keep doing so.
    assert "licensing" in assess.ASSESSMENT_AREAS[
        "licensing"
    ] or assess.ASSESSMENT_AREAS["licensing"] == ("licen",)
    assert "licensing" in assess.areas_covered(british)
    assert "licensing" in assess.areas_covered(american)
