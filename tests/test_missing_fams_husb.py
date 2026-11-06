# /src/tests/test_missing_fams_husb.py

from ged_xrefrepair.analyzer.reference_analyzer import (
    ReferenceAnalyzer
)

from ged_xrefrepair.model.gedcom_record import (
    GedcomRecord
)


def test_missing_fams_husb_detected():

    records = [

        GedcomRecord(
            xref="@I1@",
            tag="INDI",
            lines=[
                "0 @I1@ INDI",
                "1 SEX M",
            ],
        ),

        GedcomRecord(
            xref="@F1@",
            tag="FAM",
            lines=[
                "0 @F1@ FAM",
                "1 HUSB @I1@",
            ],
        ),
    ]

    analyzer = ReferenceAnalyzer()

    issues = analyzer.analyze(records)

    missing_fams = next(
        issue
        for issue in issues
        if issue.issue_type == "MISSING_FAMS_HUSB"
    )

    assert (
        missing_fams.record_id
        == "@I1@"
    )

    assert (
        missing_fams.related_xref
        == "@F1@"
    )

    assert (
        missing_fams.auto_repair_possible
        is True
    )