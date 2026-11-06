from ged_xrefrepair.analyzer.reference_analyzer import (
    ReferenceAnalyzer,
)
from ged_xrefrepair.model.gedcom_record import (
    GedcomRecord,
)


def analyze(records):
    return ReferenceAnalyzer().analyze(records)


def test_missing_family_from_fams_is_not_reported_as_missing_roles():
    records = [
        GedcomRecord(
            xref="@I1@",
            tag="INDI",
            lines=[
                "0 @I1@ INDI",
                "1 SEX M",
                "1 FAMS @F404@",
            ],
        ),
    ]

    issues = analyze(records)
    issue_types = [issue.issue_type for issue in issues]

    assert issue_types == ["MISSING_FAMILY"]
    assert issues[0].record_id == "@I1@"
    assert issues[0].related_xref == "@F404@"


def test_missing_spouse_person_is_not_reported_as_missing_fams():
    records = [
        GedcomRecord(
            xref="@F1@",
            tag="FAM",
            lines=[
                "0 @F1@ FAM",
                "1 HUSB @I404@",
                "1 WIFE @I405@",
            ],
        ),
    ]

    issues = analyze(records)

    assert [issue.issue_type for issue in issues] == [
        "MISSING_PERSON",
        "MISSING_PERSON",
    ]
    assert [issue.related_xref for issue in issues] == [
        "@I404@",
        "@I405@",
    ]
    assert all(not issue.auto_repair_possible for issue in issues)


def test_multiple_husb_candidates_are_kept_and_not_auto_repaired():
    records = [
        GedcomRecord(
            xref="@I1@",
            tag="INDI",
            lines=[
                "0 @I1@ INDI",
                "1 SEX M",
                "1 FAMS @F1@",
            ],
        ),
        GedcomRecord(
            xref="@I2@",
            tag="INDI",
            lines=[
                "0 @I2@ INDI",
                "1 SEX M",
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

    issues = analyze(records)
    husb_issues = [
        issue
        for issue in issues
        if issue.issue_type == "MISSING_HUSB"
    ]

    assert len(husb_issues) == 2
    assert {issue.related_xref for issue in husb_issues} == {
        "@I1@",
        "@I2@",
    }
    assert all(not issue.auto_repair_possible for issue in husb_issues)
    assert all("mehrere" in issue.description.lower() for issue in husb_issues)


def test_multiple_wife_candidates_are_kept_and_not_auto_repaired():
    records = [
        GedcomRecord(
            xref="@I1@",
            tag="INDI",
            lines=[
                "0 @I1@ INDI",
                "1 SEX F",
                "1 FAMS @F1@",
            ],
        ),
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

    issues = analyze(records)
    wife_issues = [
        issue
        for issue in issues
        if issue.issue_type == "MISSING_WIFE"
    ]

    assert len(wife_issues) == 2
    assert {issue.related_xref for issue in wife_issues} == {
        "@I1@",
        "@I2@",
    }
    assert all(not issue.auto_repair_possible for issue in wife_issues)
    assert all("mehrere" in issue.description.lower() for issue in wife_issues)


def test_single_husb_candidate_remains_auto_repairable():
    records = [
        GedcomRecord(
            xref="@I1@",
            tag="INDI",
            lines=[
                "0 @I1@ INDI",
                "1 SEX M",
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

    issues = analyze(records)
    husb_issue = next(
        issue
        for issue in issues
        if issue.issue_type == "MISSING_HUSB"
    )

    assert husb_issue.auto_repair_possible is True
