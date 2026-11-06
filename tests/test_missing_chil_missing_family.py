from ged_xrefrepair.analyzer.reference_analyzer import (
    ReferenceAnalyzer
)

from ged_xrefrepair.model.gedcom_record import (
    GedcomRecord
)


def test_missing_family_detected():

    records = [

        GedcomRecord(
            xref="@I1@",
            tag="INDI",
            lines=[
                "0 @I1@ INDI",
                "1 FAMC @F999@",
            ],
        ),
    ]

    analyzer = ReferenceAnalyzer()

    issues = analyzer.analyze(records)

    assert len(issues) == 1

    issue = issues[0]

    assert issue.issue_type == "MISSING_FAMILY"

    assert issue.record_id == "@I1@"

    assert issue.related_xref == "@F999@"

    assert issue.auto_repair_possible is False