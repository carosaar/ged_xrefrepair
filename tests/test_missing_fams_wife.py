from ged_xrefrepair.analyzer.reference_analyzer import (
    ReferenceAnalyzer
)

from ged_xrefrepair.model.gedcom_record import (
    GedcomRecord
)


def test_missing_fams_wife_detected():

    records = [

        GedcomRecord(
            xref="@I2@",
            tag="INDI",
            lines=[
                "0 @I2@ INDI",
                "1 SEX F",
            ],
        ),

        GedcomRecord(
            xref="@F1@",
            tag="FAM",
            lines=[
                "0 @F1@ FAM",
                "1 WIFE @I2@",
            ],
        ),
    ]

    analyzer = ReferenceAnalyzer()

    issues = analyzer.analyze(records)

    missing_fams = next(
        issue
        for issue in issues
        if issue.issue_type == "MISSING_FAMS_WIFE"
    )

    assert (
        missing_fams.record_id
        == "@I2@"
    )

    assert (
        missing_fams.related_xref
        == "@F1@"
    )

    assert (
        missing_fams.auto_repair_possible
        is True
    )