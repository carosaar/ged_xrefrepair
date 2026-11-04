from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
)
from ged_xrefrepair.services.analysis_service import AnalysisService

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.gedcom_file = None

        self.setWindowTitle("GED XRef Repair")
        self.resize(1200, 800)

        self._create_ui()

    def _create_ui(self) -> None:

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        title = QLabel("GED XRef Repair")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.file_label = QLabel(
            "Keine GEDCOM-Datei ausgewählt"
        )

        self.open_button = QPushButton(
            "GEDCOM-Datei öffnen"
        )

        self.analyze_button = QPushButton(
            "Analyse starten"
        )

        self.analyze_button.setEnabled(False)

        layout.addWidget(title)
        layout.addWidget(self.file_label)
        layout.addWidget(self.open_button)
        layout.addWidget(self.analyze_button)
        layout.addStretch()

        self.open_button.clicked.connect(
            self.select_file
        )

        self.analyze_button.clicked.connect(
            self.start_analysis
        )

        self.statusBar().showMessage(
            "Bereit"
        )

    def select_file(self) -> None:

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "GEDCOM-Datei auswählen",
            "",
            "GEDCOM Dateien (*.ged *.gedcom)"
        )

        if not filename:
            return

        self.gedcom_file = filename

        self.file_label.setText(filename)

        self.analyze_button.setEnabled(True)

        self.statusBar().showMessage(
            "Datei geladen"
        )

    def start_analysis(self) -> None:

        service = AnalysisService()

        result = service.analyze(
            self.gedcom_file
        )

        issue_text = ""

        for issue in result.issues:
            issue_text += (
                f"\n{issue.issue_type}: "
                f"{issue.description}"
            )

        QMessageBox.information(
            self,
            "Analyse",
            (
                f"Personen: {result.individuals}\n"
                f"Familien: {result.families}\n"
                f"Datensätze: {result.records}\n"
                f"Probleme: {result.issues_count}\n"
                f"{issue_text}"
            )
        )
