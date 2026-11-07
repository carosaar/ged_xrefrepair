import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from PySide6.QtWidgets import QApplication

from ged_xrefrepair.gui.main_window import MainWindow
from ged_xrefrepair.model.gedcom_record import GedcomRecord
from ged_xrefrepair.model.issue import Issue
from ged_xrefrepair.services.name_resolver import NameResolver


@pytest.fixture(scope="module")
def application():
    return QApplication.instance() or QApplication([])


def build_name_resolver():
    return NameResolver(
        [
            GedcomRecord(
                xref="@I17@",
                tag="INDI",
                lines=[
                    "0 @I17@ INDI",
                    "1 NAME Max /Mustermann/",
                    "1 BIRT",
                    "2 DATE 12.03.1890",
                    "1 DEAT",
                    "2 DATE 21.04.1968",
                ],
            ),
            GedcomRecord(
                xref="@I18@",
                tag="INDI",
                lines=[
                    "0 @I18@ INDI",
                    "1 NAME Anna /Beispiel/",
                ],
            ),
            GedcomRecord(
                xref="@F3@",
                tag="FAM",
                lines=[
                    "0 @F3@ FAM",
                    "1 HUSB @I17@",
                    "1 WIFE @I18@",
                    "1 MARR",
                    "2 DATE 14.06.1915",
                ],
            ),
        ]
    )


def select_issue(window, issue):
    window.name_resolver = build_name_resolver()
    window.populate_issue_table([issue])
    window.issue_table.setCurrentCell(0, 0)
    return window.detail_view.toPlainText()


def test_missing_chil_details_prioritize_resolved_records_and_preview(
    application,
):
    window = MainWindow()
    details = select_issue(
        window,
        Issue(
            issue_type="MISSING_CHIL",
            record_id="@F3@",
            related_xref="@I17@",
            description="Internal detail not shown",
            auto_repair_possible=True,
        ),
    )

    assert details.index("Max Mustermann") < details.index("@I17@")
    assert details.index("Anna Beispiel") < details.index("@F3@")
    assert "12.03.1890" in details
    assert "21.04.1968" in details
    assert "14.06.1915" in details
    assert "Fehlender Kind-Verweis in der Familie" in details
    assert "(MISSING_CHIL)" in details
    assert "Die ausgewählte Person verweist über einen FAMC-Eintrag" in details
    assert "Es wird ein fehlender Gegenverweis ergänzt." in details
    assert "Zieldatensatz:" in details
    assert "1 CHIL @I17@" in details
    assert "Internal detail not shown" not in details
    window.close()


def test_missing_person_details_explain_manual_resolution(
    application,
):
    window = MainWindow()
    details = select_issue(
        window,
        Issue(
            issue_type="MISSING_PERSON",
            record_id="@F3@",
            related_xref="@I404@",
            description="Internal detail not shown",
        ),
    )

    assert "Max Mustermann" in details
    assert "Person nicht vorhanden" in details
    assert details.index("Person nicht vorhanden") < details.index("@I404@")
    assert "Verweis auf eine nicht vorhandene Person" in details
    assert "(MISSING_PERSON)" in details
    assert "Mögliche Ursachen sind ein gelöschter Personendatensatz" in details
    assert "Für diesen Fehler ist keine automatische Reparatur möglich." in details
    assert "Bitte prüfen Sie die Quelldaten" in details
    window.close()
