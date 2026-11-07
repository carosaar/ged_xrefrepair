import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from ged_xrefrepair.gui.main_window import MainWindow


@pytest.fixture(scope="module")
def application():
    return QApplication.instance() or QApplication([])


def test_help_button_opens_one_modeless_owned_overview_before_info(
    application,
):
    window = MainWindow()
    window.show()
    application.processEvents()

    assert window.help_button.text() == "❓ HILFE"
    assert (
        window.help_button.geometry().right()
        < window.info_button.geometry().left()
    )

    window.help_button.click()
    application.processEvents()
    overview = window.problem_overview_window

    assert overview is not None
    assert overview.isVisible()
    assert overview.isWindow()
    assert overview.parentWidget() is window
    assert not overview.isModal()
    assert overview.problem_table.rowCount() == 8
    assert [
        overview.problem_table.item(row, 0).text()
        for row in range(overview.problem_table.rowCount())
    ] == [
        "MISSING_CHIL",
        "MISSING_FAMC",
        "MISSING_HUSB",
        "MISSING_WIFE",
        "MISSING_FAMS_HUSB",
        "MISSING_FAMS_WIFE",
        "MISSING_PERSON",
        "MISSING_FAMILY",
    ]
    assert "PEDI" in overview.problem_table.item(0, 3).text()
    assert "PEDI" in overview.problem_table.item(1, 3).text()
    assert "CHIL" in overview.problem_table.item(6, 1).text()
    assert max(
        overview.problem_table.rowHeight(row)
        for row in range(overview.problem_table.rowCount())
    ) <= 80
    assert sum(
        overview.problem_table.rowHeight(row)
        for row in range(overview.problem_table.rowCount())
    ) <= overview.problem_table.viewport().height()

    window.help_button.click()
    application.processEvents()
    assert window.problem_overview_window is overview

    window.close()
    application.processEvents()
    assert not overview.isVisible()
