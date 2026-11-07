# tests/test_missing_chil.py

import pytest

from ged_xrefrepair.analyzer.reference_analyzer import (
    ReferenceAnalyzer
)
from ged_xrefrepair.model.gedcom_record import (
    GedcomRecord
)


def test_missing_chil_detected():

    records = [

        GedcomRecord(
            xref="@I1@",
            tag="INDI",
            lines=[
                "0 @I1@ INDI",
                "1 FAMC @F1@",
            ],
        ),

        GedcomRecord(
            xref="@F1@",
            tag="FAM",
            lines=[
                "0 @F1@ FAM",
            ],
        ),
    ]

    analyzer = ReferenceAnalyzer()

    issues = analyzer.analyze(records)

    assert len(issues) == 1

    issue = issues[0]

    assert issue.issue_type == "MISSING_CHIL"

    assert issue.record_id == "@F1@"

    assert issue.related_xref == "@I1@"

    assert issue.auto_repair_possible is True


@pytest.mark.parametrize(
    "pedi_value",
    [None, "", "BIRTH", "ADOPTED", "FOSTER", "OTHER"],
)
def test_missing_chil_checks_famc_regardless_of_pedi(pedi_value):
    individual_lines = [
        "0 @I1@ INDI",
        "1 FAMC @F1@",
    ]
    if pedi_value is not None:
        pedi_line = "2 PEDI"
        if pedi_value:
            pedi_line += f" {pedi_value}"
        individual_lines.append(pedi_line)

    records = [
        GedcomRecord(
            xref="@I1@",
            tag="INDI",
            lines=individual_lines,
        ),
        GedcomRecord(
            xref="@F1@",
            tag="FAM",
            lines=[
                "0 @F1@ FAM",
            ],
        ),
    ]

    issues = ReferenceAnalyzer().analyze(records)

    assert any(
        issue.issue_type == "MISSING_CHIL"
        for issue in issues
    )


def test_missing_family_is_still_reported_for_adopted_famc():
    records = [
        GedcomRecord(
            xref="@I1@",
            tag="INDI",
            lines=[
                "0 @I1@ INDI",
                "1 FAMC @F404@",
                "2 PEDI ADOPTED",
            ],
        ),
    ]

    issues = ReferenceAnalyzer().analyze(records)

    assert [issue.issue_type for issue in issues] == ["MISSING_FAMILY"]


def test_duplicate_famc_relationship_is_reported_once_regardless_of_pedi():
    records = [
        GedcomRecord(
            xref="@I1@",
            tag="INDI",
            lines=[
                "0 @I1@ INDI",
                "1 FAMC @F1@",
                "2 PEDI ADOPTED",
                "1 FAMC @F1@",
                "2 PEDI BIRTH",
            ],
        ),
        GedcomRecord(
            xref="@F1@",
            tag="FAM",
            lines=[
                "0 @F1@ FAM",
            ],
        ),
    ]

    issues = ReferenceAnalyzer().analyze(records)

    assert [issue.issue_type for issue in issues] == ["MISSING_CHIL"]