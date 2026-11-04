from PySide6.QtWidgets import QApplication
from ged_xrefrepair.gui.main_window import MainWindow

import sys


def main() -> None:
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
