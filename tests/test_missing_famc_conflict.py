# tests/test_missing_famc_conflict.py

from ged_xrefrepair.analyzer.reference_analyzer import (
    ReferenceAnalyzer
)

from ged_xrefrepair.model.gedcom_record import (
    GedcomRecord
)


def test_missing_famc_not_auto_repairable_if_person_already_has_other_family():

    records = [

        GedcomRecord(
            xref="@I1@",
            tag="INDI",
            lines=[
                "0 @I1@ INDI",
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
            ],
        ),
    ]

    analyzer = ReferenceAnalyzer()

    issues = analyzer.analyze(records)

    missing_famc = next(
        issue
        for issue in issues
        if issue.issue_type == "MISSING_FAMC"
    )

    assert (
        missing_famc.record_id
        == "@I1@"
    )

    assert (
        missing_famc.related_xref
        == "@F1@"
    )

    assert (
        missing_famc.auto_repair_possible
        is False
    )