import pytest

from ged_xrefrepair.analyzer.reference_analyzer import (
    ReferenceAnalyzer,
)
from ged_xrefrepair.model.gedcom_record import (
    GedcomRecord,
)


@pytest.mark.parametrize(
    ("existing_family", "pedi_value", "expected_issue", "auto_repair"),
    [
        ("@F2@", "ADOPTED", True, True),
        ("@F2@", "FOSTER", True, True),
        ("@F2@", "OTHER", True, True),
        ("@F2@", "BIRTH", True, True),
        ("@F2@", "", True, True),
        ("@F1@", None, False, False),
        ("@F1@", "ADOPTED", False, False),
        ("@F1@", "BIRTH", False, False),
    ],
)
def test_missing_famc_matches_family_regardless_of_pedi(
    existing_family,
    pedi_value,
    expected_issue,
    auto_repair,
):
    person_lines = [
        "0 @I1@ INDI",
        f"1 FAMC {existing_family}",
    ]
    if pedi_value is not None:
        pedi_line = "2 PEDI"
        if pedi_value:
            pedi_line += f" {pedi_value}"
        person_lines.append(pedi_line)

    records = [
        GedcomRecord(
            xref="@I1@",
            tag="INDI",
            lines=person_lines,
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

    issues = ReferenceAnalyzer().analyze(records)
    missing_famc = [
        issue
        for issue in issues
        if issue.issue_type == "MISSING_FAMC"
    ]

    assert bool(missing_famc) is expected_issue
    if expected_issue:
        assert len(missing_famc) == 1
        assert missing_famc[0].record_id == "@I1@"
        assert missing_famc[0].related_xref == "@F1@"
        assert missing_famc[0].auto_repair_possible is auto_repair


def test_adopted_famc_to_same_family_prevents_missing_famc():
    records = [
        GedcomRecord(
            xref="@I1@",
            tag="INDI",
            lines=[
                "0 @I1@ INDI",
                "1 FAMC @F1@",
                "2 PEDI ADOPTED",
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

    issues = ReferenceAnalyzer().analyze(records)
    assert not any(
        issue.issue_type == "MISSING_FAMC"
        for issue in issues
    )
