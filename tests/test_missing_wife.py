# /src/tests/test_missing_wife.py

from ged_xrefrepair.analyzer.reference_analyzer import (
    ReferenceAnalyzer
)

from ged_xrefrepair.model.gedcom_record import (
    GedcomRecord
)


def test_missing_wife_detected():

    records = [

        GedcomRecord(
            xref="@I2@",
            tag="INDI",
            lines=[
                "0 @I2@ INDI",
                "1 SEX F",
                "1 FAMS @F1@",
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

    missing_wife = next(
        issue
        for issue in issues
        if issue.issue_type == "MISSING_WIFE"
    )

    assert (
        missing_wife.record_id
        == "@F1@"
    )

    assert (
        missing_wife.related_xref
        == "@I2@"
    )

    assert (
        missing_wife.auto_repair_possible
        is True
    )