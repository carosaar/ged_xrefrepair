# src/tests/test_multiple_famc.py

from ged_xrefrepair.analyzer.reference_analyzer import (
    ReferenceAnalyzer
)

from ged_xrefrepair.model.gedcom_record import (
    GedcomRecord
)


def analyze_multiple_famc(
    famc_entries: list[tuple[str, str | None]],
):
    individual_lines = ["0 @I1@ INDI"]
    records = []

    for family_xref, pedi_value in famc_entries:
        individual_lines.append(
            f"1 FAMC {family_xref}"
        )
        if pedi_value is not None:
            pedi_line = "2 PEDI"
            if pedi_value:
                pedi_line += f" {pedi_value}"
            individual_lines.append(pedi_line)

        records.append(
            GedcomRecord(
                xref=family_xref,
                tag="FAM",
                lines=[
                    f"0 {family_xref} FAM",
                    "1 CHIL @I1@",
                ],
            )
        )

    records.insert(
        0,
        GedcomRecord(
            xref="@I1@",
            tag="INDI",
            lines=individual_lines,
        ),
    )

    issues = ReferenceAnalyzer().analyze(records)
    return [
        issue
        for issue in issues
        if issue.issue_type == "MULTIPLE_FAMC"
    ]


def test_multiple_famc_detected():

    records = [

        GedcomRecord(
            xref="@I1@",
            tag="INDI",
            lines=[
                "0 @I1@ INDI",
                "1 FAMC @F1@",
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
                "1 CHIL @I1@",
            ],
        ),
    ]

    analyzer = ReferenceAnalyzer()

    issues = analyzer.analyze(records)

    multiple_famc = [
        issue
        for issue in issues
        if issue.issue_type == "MULTIPLE_FAMC"
    ]

    assert len(multiple_famc) == 1

    issue = multiple_famc[0]

    assert issue.record_id == "@I1@"

    assert issue.auto_repair_possible is False


def test_multiple_famc_ignores_non_birth_pedi():
    issues = analyze_multiple_famc(
        [
            ("@F1@", "BIRTH"),
            ("@F2@", "ADOPTED"),
        ]
    )

    assert issues == []


def test_multiple_famc_ignores_multiple_non_birth_pedi():
    issues = analyze_multiple_famc(
        [
            ("@F1@", "ADOPTED"),
            ("@F2@", "FOSTER"),
        ]
    )

    assert issues == []


def test_multiple_famc_counts_birth_and_unspecified_pedi():
    issues = analyze_multiple_famc(
        [
            ("@F1@", "BIRTH"),
            ("@F2@", None),
        ]
    )

    assert len(issues) == 1


def test_multiple_famc_counts_empty_pedi_as_birth():
    issues = analyze_multiple_famc(
        [
            ("@F1@", "BIRTH"),
            ("@F2@", ""),
        ]
    )

    assert len(issues) == 1