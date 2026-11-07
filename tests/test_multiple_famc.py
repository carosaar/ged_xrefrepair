# src/tests/test_multiple_famc.py

import pytest

from ged_xrefrepair.analyzer.reference_analyzer import (
    ReferenceAnalyzer
)

from ged_xrefrepair.model.gedcom_record import (
    GedcomRecord
)


def analyze_famc_relationships(
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

    return ReferenceAnalyzer().analyze(records)


@pytest.mark.parametrize(
    "famc_entries",
    [
        [("@F1@", None), ("@F2@", None)],
        [("@F1@", "BIRTH"), ("@F2@", "BIRTH")],
        [("@F1@", "BIRTH"), ("@F2@", "")],
        [("@F1@", "BIRTH"), ("@F2@", "ADOPTED")],
        [("@F1@", "BIRTH"), ("@F2@", "FOSTER")],
        [("@F1@", "ADOPTED"), ("@F2@", "FOSTER")],
    ],
)
def test_multiple_famc_is_not_reported(famc_entries):
    issues = analyze_famc_relationships(famc_entries)

    assert all(
        issue.issue_type != "MULTIPLE_FAMC"
        for issue in issues
    )