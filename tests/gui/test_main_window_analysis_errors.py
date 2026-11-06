import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from ged_xrefrepair.gui.main_window import MainWindow
from ged_xrefrepair.services.analysis_service import AnalysisService


@pytest.fixture(scope="module")
def application():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize(
    ("error", "expected_message"),
    [
        (FileNotFoundError("missing.ged"), "konnte nicht geöffnet"),
        (UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte"), "nicht als UTF-8 lesbar"),
    ],
)
def test_analysis_error_clears_previous_results(
    application,
    monkeypatch,
    error,
    expected_message,
):
    window = MainWindow()
    window.gedcom_file = "new.ged"
    window.current_issues = [object()]
    window.name_resolver = object()
    window.persons_value.setText("10")
    window.families_value.setText("5")
    window.records_value.setText("15")
    window.issues_value.setText("2")
    window.issue_table.setRowCount(1)
    window.detail_view.setPlainText("Old result")
    window.selected_count_label.setText("Ausgewählt: 1")
    window.repair_button.setEnabled(True)
    window.save_button.setEnabled(True)

    def fail_analysis(self, filename):
        raise error

    messages = []
    monkeypatch.setattr(AnalysisService, "analyze", fail_analysis)
    monkeypatch.setattr(
        QMessageBox,
        "critical",
        lambda parent, title, message: messages.append((title, message)),
    )

    window.start_analysis()

    assert window.current_issues == []
    assert window.name_resolver is None
    assert window.persons_value.text() == "-"
    assert window.families_value.text() == "-"
    assert window.records_value.text() == "-"
    assert window.issues_value.text() == "-"
    assert window.issue_table.rowCount() == 0
    assert window.detail_view.toPlainText() == ""
    assert window.selected_count_label.text() == "Ausgewählt: 0"
    assert not window.repair_button.isEnabled()
    assert not window.save_button.isEnabled()
    assert expected_message in messages[0][1]
    assert window.statusBar().currentMessage() == "Analyse fehlgeschlagen"
    window.close()
