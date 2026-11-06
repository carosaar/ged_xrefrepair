# src/tests/test_multiple_famc.py

from ged_xrefrepair.analyzer.reference_analyzer import (
    ReferenceAnalyzer
)

from ged_xrefrepair.model.gedcom_record import (
    GedcomRecord
)


def test_multiple_famc_detected():

    records = [

        GedcomRecord(
            xref="@I1@",
            tag="INDI",
            lines=[
                "0 @I1@ INDI",
                "1 FAMC @F1@",
                "1 FAMC @F2@",
            ],
        ),

        GedcomRecord(
            xref="@F1@",
            tag="FAM",
            lines=[
                "0 @F1@ FAM",
                "1 CHIL @I1@",
            ],
        ),

        GedcomRecord(
            xref="@F2@",
            tag="FAM",
            lines=[
                "0 @F2@ FAM",
                "1 CHIL @I1@",
            ],
        ),
    ]

    analyzer = ReferenceAnalyzer()

    issues = analyzer.analyze(records)

    multiple_famc = [
        issue
        for issue in issues
        if issue.issue_type == "MULTIPLE_FAMC"
    ]

    assert len(multiple_famc) == 1

    issue = multiple_famc[0]

    assert issue.record_id == "@I1@"

    assert issue.auto_repair_possible is False