from ged_xrefrepair.analyzer.reference_analyzer import (
    ReferenceAnalyzer
)

from ged_xrefrepair.model.gedcom_record import (
    GedcomRecord
)


def test_missing_famc_detected():

    records = [

        GedcomRecord(
            xref="@I1@",
            tag="INDI",
            lines=[
                "0 @I1@ INDI",
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
    ]

    analyzer = ReferenceAnalyzer()

    issues = analyzer.analyze(records)

    assert len(issues) == 1

    issue = issues[0]

    assert issue.issue_type == "MISSING_FAMC"

    assert issue.record_id == "@I1@"

    assert issue.related_xref == "@F1@"

    assert issue.auto_repair_possible is True