import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ged_xrefrepair.gui.main_window import MainWindow
from ged_xrefrepair.model.issue import Issue


@pytest.fixture(scope="module")
def application():
    return QApplication.instance() or QApplication([])


def issue_selection(window):
    selection = {}
    for row in range(window.issue_table.rowCount()):
        checkbox = window.issue_table.item(row, 0)
        issue = checkbox.data(Qt.ItemDataRole.UserRole)
        selection[issue.record_id] = (
            checkbox.checkState() == Qt.CheckState.Checked
        )
    return selection


def visible_record_ids(window):
    return {
        window.issue_table.item(row, 1).text()
        for row in range(window.issue_table.rowCount())
        if not window.issue_table.isRowHidden(row)
    }


def test_filters_and_selection_actions_only_affect_visible_issues(
    application,
):
    window = MainWindow()
    window.populate_issue_table(
        [
            Issue("TYPE_A", "A reparierbar", "@I1@", "@F1@", True),
            Issue("TYPE_A", "A nicht reparierbar", "@I2@", "@F2@", False),
            Issue("TYPE_B", "B reparierbar", "@I3@", "@F3@", True),
            Issue("TYPE_B", "B nicht reparierbar", "@I4@", "@F4@", False),
        ]
    )
    window.show()
    application.processEvents()

    assert (
        window.select_all_button.geometry().center().y()
        == window.issue_type_filter.geometry().center().y()
    )
    assert (
        window.invert_selection_button.geometry().right()
        < window.issue_type_filter.geometry().left()
    )
    assert (
        window.issue_type_filter.geometry().right()
        < window.repairability_filter.geometry().left()
    )

    assert issue_selection(window) == {
        "@I1@": False,
        "@I2@": False,
        "@I3@": False,
        "@I4@": False,
    }

    window.issue_table.item(2, 0).setCheckState(Qt.CheckState.Checked)

    window.issue_type_filter.setCurrentIndex(
        window.issue_type_filter.findData("TYPE_A")
    )
    assert visible_record_ids(window) == {"@I1@", "@I2@"}

    window.clear_all_issues()
    assert issue_selection(window) == {
        "@I1@": False,
        "@I2@": False,
        "@I3@": True,
        "@I4@": False,
    }

    window.select_all_issues()
    assert issue_selection(window) == {
        "@I1@": True,
        "@I2@": True,
        "@I3@": True,
        "@I4@": False,
    }

    window.invert_selection()
    assert issue_selection(window) == {
        "@I1@": False,
        "@I2@": False,
        "@I3@": True,
        "@I4@": False,
    }

    window.repairability_filter.setCurrentIndex(
        window.repairability_filter.findData(False)
    )
    assert visible_record_ids(window) == {"@I2@"}
    window.select_all_issues()
    assert issue_selection(window) == {
        "@I1@": False,
        "@I2@": True,
        "@I3@": True,
        "@I4@": False,
    }

    window.issue_type_filter.setCurrentIndex(0)
    assert visible_record_ids(window) == {"@I2@", "@I4@"}
    window.close()
