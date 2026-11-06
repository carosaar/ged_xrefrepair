import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from ged_xrefrepair.analyzer.analysis_result import AnalysisResult
from ged_xrefrepair.gui.main_window import MainWindow
from ged_xrefrepair.model.issue import Issue
from ged_xrefrepair.services.analysis_service import AnalysisService


@pytest.fixture(scope="module")
def application():
    return QApplication.instance() or QApplication([])


def wait_for_analysis(window, timeout_ms=5000):
    loop = QEventLoop()
    poll_timer = QTimer()
    poll_timer.setInterval(10)
    poll_timer.timeout.connect(
        lambda: loop.quit()
        if not window._analysis_in_progress
        else None
    )
    timeout_timer = QTimer()
    timeout_timer.setSingleShot(True)
    timeout_timer.timeout.connect(loop.quit)

    if window._analysis_in_progress:
        poll_timer.start()
        timeout_timer.start(timeout_ms)
        loop.exec()

    poll_timer.stop()
    timeout_timer.stop()
    assert not window._analysis_in_progress, (
        window._analysis_thread_done,
        window._analysis_display_done,
        window._issue_display_index,
        window.issue_table.rowCount(),
    )


@pytest.mark.parametrize(
    ("error", "expected_message"),
    [
        (FileNotFoundError("missing.ged"), "konnte nicht geöffnet"),
        (UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte"), "nicht als UTF-8 lesbar"),
        (RuntimeError("unexpected failure"), "unerwarteter Fehler"),
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
    wait_for_analysis(window)

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
    assert window.open_button.isEnabled()
    assert window.analyze_button.isEnabled()
    window.close()


def test_analysis_runs_in_background_and_duplicate_start_is_ignored(
    application,
    monkeypatch,
):
    window = MainWindow()
    window.gedcom_file = (
        "tests/sample_data/missing_chil.ged"
    )
    calls = []
    real_analyze = AnalysisService.analyze

    def delayed_analysis(self, filename):
        calls.append(filename)
        time.sleep(1.2)
        return real_analyze(self, filename)

    monkeypatch.setattr(
        AnalysisService,
        "analyze",
        delayed_analysis,
    )

    window.show()
    application.processEvents()
    window.start_analysis()
    assert window.statusBar().currentMessage() == "Analyse läuft..."
    assert not window.open_button.isEnabled()
    assert not window.analyze_button.isEnabled()

    window.close()
    assert window.isVisible()

    window.start_analysis()
    assert len(calls) <= 1

    ui_timer_fired = []
    QTimer.singleShot(20, lambda: ui_timer_fired.append(True))
    wait_for_analysis(window)
    assert ui_timer_fired
    assert calls == [window.gedcom_file]
    assert window.statusBar().currentMessage() == "Analyse abgeschlossen"
    assert window.open_button.isEnabled()
    assert window.analyze_button.isEnabled()
    window.close()


def test_successful_analysis_with_no_issues(
    application,
    monkeypatch,
):
    window = MainWindow()
    window.gedcom_file = "empty.ged"
    result = AnalysisResult(
        individuals=0,
        families=0,
        records=0,
        issues_count=0,
        issues=[],
        record_list=[],
    )
    monkeypatch.setattr(
        AnalysisService,
        "analyze",
        lambda self, filename: result,
    )

    window.show()
    application.processEvents()
    window.start_analysis()
    wait_for_analysis(window)

    assert window.persons_value.text() == "0"
    assert window.families_value.text() == "0"
    assert window.records_value.text() == "0"
    assert window.issues_value.text() == "0"
    assert window.issue_table.rowCount() == 0
    assert window.current_issues == []
    assert window.statusBar().currentMessage() == "Analyse abgeschlossen"
    assert window.open_button.isEnabled()
    assert window.analyze_button.isEnabled()
    window.close()
