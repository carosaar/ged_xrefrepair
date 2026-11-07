import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

from ged_xrefrepair import __version__
from ged_xrefrepair.gui.main_window import MainWindow
from ged_xrefrepair.model.gedcom_record import GedcomRecord
from ged_xrefrepair.model.issue import Issue
from ged_xrefrepair.services.name_resolver import NameResolver


@pytest.fixture(scope="module")
def application():
    return QApplication.instance() or QApplication([])


def test_repair_undo_and_save_backup_loaded_source(
    application,
    monkeypatch,
    tmp_path,
):
    source_path = tmp_path / "source.ged"
    original_content = (
        "0 @I1@ INDI\n"
        "1 FAMC @F1@\n"
        "0 @F1@ FAM\n"
    )
    source_path.write_text(original_content, encoding="utf-8")
    output_path = tmp_path / "source_repaired.ged"
    backup_path = tmp_path / "source.ged.bak"
    backup_path.write_text("stale backup", encoding="utf-8")

    window = MainWindow()
    window.gedcom_file = str(source_path)
    window.current_records = [
        GedcomRecord(
            "@I1@",
            "INDI",
            ["0 @I1@ INDI", "1 FAMC @F1@"],
        ),
        GedcomRecord("@F1@", "FAM", ["0 @F1@ FAM"]),
    ]
    issue = Issue(
        "MISSING_CHIL",
        "Internal description",
        "@F1@",
        "@I1@",
        True,
    )
    status_messages = []
    repair_confirmations = []
    window.statusBar().messageChanged.connect(status_messages.append)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args: repair_confirmations.append(args[2])
        or QMessageBox.StandardButton.Yes,
    )
    window.populate_issue_table([issue])
    window.issue_table.item(0, 0).setCheckState(Qt.CheckState.Checked)

    assert window.repair_button.isEnabled()
    window.repair_button.click()

    assert "1 CHIL @I1@" in window.current_records[1].lines
    assert window.issue_table.rowCount() == 1
    assert window.issue_table.item(0, 5).text() == "✅"
    assert window._has_unsaved_repairs
    assert window.save_button.isEnabled()
    assert window.undo_button.isEnabled()
    assert any(
        "Reparatur abgeschlossen" in message
        for message in status_messages
    )
    assert "Weiter mit Speichern" in window.statusBar().currentMessage()
    assert "1 Problem wird jetzt korrigiert" in repair_confirmations[0]
    assert source_path.read_text(encoding="utf-8") == original_content

    window.undo_button.click()
    assert "1 CHIL @I1@" not in window.current_records[1].lines
    assert window.issue_table.rowCount() == 1
    assert window.issue_table.item(0, 5).text() == ""
    assert not window.undo_button.isEnabled()
    assert window.statusBar().currentMessage() == "Änderungen rückgängig gemacht"

    window.issue_table.item(0, 0).setCheckState(Qt.CheckState.Checked)
    window.repair_button.click()
    assert "1 CHIL @I1@" in window.current_records[1].lines
    assert window.undo_button.isEnabled()
    assert window.issue_table.item(0, 5).text() == "✅"

    warnings = []
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args: (str(source_path), "GEDCOM Dateien (*.ged)"),
    )
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda *args: warnings.append(args[2]),
    )
    window.save_repaired_file()

    assert warnings
    assert source_path.read_text(encoding="utf-8") == original_content
    assert window._has_unsaved_repairs

    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args: (str(output_path), "GEDCOM Dateien (*.ged)"),
    )
    window.save_repaired_file()

    assert output_path.read_text(encoding="utf-8") == (
        "0 @I1@ INDI\n"
        "1 FAMC @F1@\n"
        "0 @F1@ FAM\n"
        "1 CHIL @I1@\n"
    )
    assert backup_path.read_text(encoding="utf-8") == original_content
    assert f"Sicherung erstellt: {backup_path.name}" in status_messages
    assert source_path.read_text(encoding="utf-8") == original_content
    assert not window._has_unsaved_repairs
    assert not window.save_button.isEnabled()
    assert window.statusBar().currentMessage() == "Datei gespeichert"
    window.close()


def test_existing_output_requires_confirmation_before_backup_or_write(
    application,
    monkeypatch,
    tmp_path,
):
    source_path = tmp_path / "source.ged"
    output_path = tmp_path / "existing.ged"
    source_path.write_text("original source", encoding="utf-8")
    output_path.write_text("existing output", encoding="utf-8")

    window = MainWindow()
    window.gedcom_file = str(source_path)
    window.current_records = [
        GedcomRecord("@I1@", "INDI", ["0 @I1@ INDI"])
    ]
    window._has_unsaved_repairs = True
    questions = []
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args: (str(output_path), "GEDCOM Dateien (*.ged)"),
    )
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args: questions.append(args) or QMessageBox.StandardButton.No,
    )

    window.save_repaired_file()

    assert questions
    assert output_path.read_text(encoding="utf-8") == "existing output"
    assert not (tmp_path / "source.ged.bak").exists()
    assert window._has_unsaved_repairs
    window.close()


@pytest.mark.parametrize(
    ("repair_status", "expected_text"),
    [
        ("REPAIRED", "Reparatur durchgeführt"),
        ("SKIPPED", "Keine Änderung erforderlich"),
        ("FAILED", "Reparatur fehlgeschlagen"),
    ],
)
def test_repair_status_is_shown_in_details(
    application,
    repair_status,
    expected_text,
):
    window = MainWindow()
    window.current_records = [
        GedcomRecord(
            "@I1@",
            "INDI",
            ["0 @I1@ INDI", "1 FAMC @F1@"],
        ),
        GedcomRecord("@F1@", "FAM", ["0 @F1@ FAM"]),
    ]
    window.name_resolver = NameResolver(window.current_records)
    issue = Issue(
        "MISSING_CHIL",
        "Fehlender Kind-Verweis",
        "@F1@",
        "@I1@",
        True,
        repair_status,
    )

    window.populate_issue_table([issue])
    window.issue_table.setCurrentCell(0, 0)
    window.show_issue_details()

    assert window.issue_table.item(0, 5).text() in {
        "✅",
        "⚠",
        "❌",
    }
    assert expected_text in window.detail_view.toPlainText()
    if repair_status == "REPAIRED":
        assert "1 CHIL @I1@" in window.detail_view.toPlainText()
    window.close()


def test_nonrepairable_issue_has_no_success_status(application):
    window = MainWindow()
    issue = Issue(
        "MISSING_PERSON",
        "Fehlende Person",
        "@F1@",
        "@I404@",
        False,
    )

    window.populate_issue_table([issue])

    assert window.issue_table.item(0, 5).text() == "—"
    window.close()


def test_repair_round_summary_reports_skipped_and_failed_issues(
    application,
    monkeypatch,
):
    window = MainWindow()
    window.current_records = [
        GedcomRecord("@F1@", "FAM", ["0 @F1@ FAM", "1 CHIL @I1@"]),
        GedcomRecord(
            "@I1@",
            "INDI",
            ["0 @I1@ INDI", "1 FAMC @F1@"],
        ),
    ]
    skipped = Issue(
        "MISSING_CHIL",
        "Already present",
        "@F1@",
        "@I1@",
        True,
    )
    failed = Issue(
        "MISSING_CHIL",
        "Missing target",
        "@F404@",
        "@I1@",
        True,
    )
    confirmations = []
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args: confirmations.append(args[2])
        or QMessageBox.StandardButton.Yes,
    )

    window.populate_issue_table([skipped, failed])
    window.issue_table.item(0, 0).setCheckState(Qt.CheckState.Checked)
    window.issue_table.item(1, 0).setCheckState(Qt.CheckState.Checked)
    window.apply_selected_repairs()

    assert skipped.repair_status == "SKIPPED"
    assert failed.repair_status == "FAILED"
    assert window.statusBar().currentMessage() == (
        "Reparatur abgeschlossen: 0 Reparaturen durchgeführt, "
        "1 Reparatur übersprungen, 1 Fehler. Weiter mit Speichern"
    )
    assert "2 Probleme werden jetzt korrigiert" in confirmations[0]
    assert window.issue_table.rowCount() == 2
    window.close()


def test_declining_repair_confirmation_keeps_records_unchanged(
    application,
    monkeypatch,
):
    window = MainWindow()
    window.current_records = [
        GedcomRecord("@F1@", "FAM", ["0 @F1@ FAM"]),
        GedcomRecord(
            "@I1@",
            "INDI",
            ["0 @I1@ INDI", "1 FAMC @F1@"],
        ),
    ]
    issue = Issue(
        "MISSING_CHIL",
        "Missing child link",
        "@F1@",
        "@I1@",
        True,
    )
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args: QMessageBox.StandardButton.No,
    )

    window.populate_issue_table([issue])
    window.issue_table.item(0, 0).setCheckState(Qt.CheckState.Checked)
    window.apply_selected_repairs()

    assert window.current_records[0].lines == ["0 @F1@ FAM"]
    assert issue.repair_status == "NOT_PROCESSED"
    assert not window.repair_service.can_undo
    window.close()


def test_save_records_repaired_count_in_head(tmp_path, application, monkeypatch):
    source_path = tmp_path / "source.ged"
    output_path = tmp_path / "repaired.ged"
    source_path.write_text("0 HEAD\n", encoding="utf-8")
    window = MainWindow()
    window.gedcom_file = str(source_path)
    window.current_records = [
        GedcomRecord("@HEAD@", "HEAD", ["0 HEAD"]),
        GedcomRecord("@F1@", "FAM", ["0 @F1@ FAM"]),
        GedcomRecord(
            "@I1@",
            "INDI",
            ["0 @I1@ INDI", "1 FAMC @F1@"],
        ),
    ]
    issue = Issue(
        "MISSING_CHIL",
        "Missing child link",
        "@F1@",
        "@I1@",
        True,
    )
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args: QMessageBox.StandardButton.Yes,
    )
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args: (str(output_path), "GEDCOM Dateien (*.ged)"),
    )

    window.populate_issue_table([issue])
    window.issue_table.item(0, 0).setCheckState(Qt.CheckState.Checked)
    window.apply_selected_repairs()
    window.save_repaired_file()

    saved_lines = output_path.read_text(encoding="utf-8").splitlines()
    assert (
        f"1 NOTE ged_XRefRepair {__version__}: am "
        in saved_lines[1]
    )
    assert saved_lines[1].endswith("1 Zeigerreparaturen durchgeführt")
    assert "1 CHIL @I1@" in saved_lines
    window.close()


def test_repair_log_button_opens_read_only_log_window(
    tmp_path,
    application,
    monkeypatch,
):
    gedcom_path = tmp_path / "Familie.ged"
    output_path = tmp_path / "Familie_repaired.ged"
    gedcom_path.write_text("0 HEAD\n", encoding="utf-8")
    window = MainWindow()
    window.gedcom_file = str(gedcom_path)
    window.current_records = [
        GedcomRecord("@HEAD@", "HEAD", ["0 HEAD"]),
        GedcomRecord("@F1@", "FAM", ["0 @F1@ FAM"]),
        GedcomRecord(
            "@I1@",
            "INDI",
            ["0 @I1@ INDI", "1 FAMC @F1@"],
        ),
    ]
    issue = Issue(
        "MISSING_CHIL",
        "Missing child link",
        "@F1@",
        "@I1@",
        True,
    )
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args: QMessageBox.StandardButton.Yes,
    )
    assert not window.repair_log_button.isEnabled()

    window.populate_issue_table([issue])
    window.issue_table.item(0, 0).setCheckState(Qt.CheckState.Checked)
    window.apply_selected_repairs()

    log_path = tmp_path / "Familie_repaired.ged.repair.log"
    assert not log_path.exists()
    assert window.repair_log_button.isEnabled()
    window.repair_log_button.click()

    assert window.repair_log_window is not None
    assert window.repair_log_window.windowTitle() == (
        "ged_XrefRepair - Reparaturprotokoll"
    )
    assert window.repair_log_window.text_edit.isReadOnly()
    assert "Eingefügte Zeile: 1 CHIL @I1@" in (
        window.repair_log_window.text_edit.toPlainText()
    )
    assert not window.repair_log_window.save_button.isEnabled()
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args: (str(output_path), "GEDCOM Dateien (*.ged)"),
    )
    window.save_repaired_file()
    assert log_path.is_file()
    assert window.repair_log_window.save_button.isEnabled()

    saved_log_path = tmp_path / "archiv" / "Familie.repair.log"
    saved_log_path.parent.mkdir()
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args: (str(saved_log_path), "Protokolldateien (*.log)"),
    )
    information_messages = []
    monkeypatch.setattr(
        QMessageBox,
        "information",
        lambda *args: information_messages.append(args[2]),
    )
    window.repair_log_window.save_button.click()

    assert saved_log_path.read_text(encoding="utf-8") == log_path.read_text(
        encoding="utf-8"
    )
    assert information_messages
    saved_log = log_path.read_text(encoding="utf-8")
    window.undo_button.click()
    assert log_path.read_text(encoding="utf-8") == saved_log
    window.close()
