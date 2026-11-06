# tests/test_missing_chil.py

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