from collections import Counter
from pathlib import Path

from ged_xrefrepair.services.analysis_service import AnalysisService


def test_combined_gedcom_detects_all_problem_types():
    gedcom_file = (
        Path(__file__).parent
        / "sample_data"
        / "TEST_00_ALL_PROBLEMS.ged"
    )

    result = AnalysisService().analyze(str(gedcom_file))

    assert Counter(
        issue.issue_type
        for issue in result.issues
    ) == {
        "MISSING_CHIL": 3,
        "MISSING_FAMILY": 2,
        "MISSING_FAMC": 3,
        "MISSING_PERSON": 2,
        "MISSING_FAMS_HUSB": 1,
        "MISSING_FAMS_WIFE": 1,
        "MISSING_HUSB": 7,
        "MISSING_WIFE": 7,
    }
    assert result.records == 38
    assert result.individuals == 17
    assert result.families == 19
    assert result.issues_count == 26

    assert all(
        not issue.auto_repair_possible
        for issue in result.issues
        if issue.issue_type in {
            "MISSING_FAMILY",
            "MISSING_PERSON",
        }
    )
    assert all(
        issue.issue_type != "MULTIPLE_FAMC"
        for issue in result.issues
    )
    assert all(
        issue.auto_repair_possible
        for issue in result.issues
        if issue.issue_type in {"MISSING_CHIL", "MISSING_FAMC"}
    )
