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

    assert len(issues) == 1

    issue = issues[0]

    assert issue.issue_type == "MISSING_CHIL"

    #
    # Laut repair_rules.md:
    # Kind existiert bereits als CHIL
    # in anderer Familie.
    #
    assert issue.auto_repair_possible is False