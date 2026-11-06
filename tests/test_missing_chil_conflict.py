from ged_xrefrepair.analyzer.reference_analyzer import (
    ReferenceAnalyzer
)

from ged_xrefrepair.model.gedcom_record import (
    GedcomRecord
)


def test_missing_chil_not_auto_repairable_if_child_exists_in_other_family():

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

    #
    # Es müssen nun zwei Issues entstehen:
    # MISSING_CHIL und MISSING_FAMC
    #

    assert len(issues) == 2

    missing_chil = next(
        issue
        for issue in issues
        if issue.issue_type == "MISSING_CHIL"
    )

    missing_famc = next(
        issue
        for issue in issues
        if issue.issue_type == "MISSING_FAMC"
    )

    #
    # MISSING_CHIL
    #

    assert missing_chil.record_id == "@F1@"

    assert missing_chil.related_xref == "@I1@"

    assert (
        missing_chil.auto_repair_possible
        is False
    )

    #
    # MISSING_FAMC
    #

    assert missing_famc.record_id == "@I1@"

    assert missing_famc.related_xref == "@F2@"

    assert (
        missing_famc.auto_repair_possible
        is False
    )