# src/ged_xrefrepair/gui/main_window.py

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

from ged_xrefrepair.services.analysis_service import AnalysisService


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()

        self.gedcom_file = None

        self.setWindowTitle("GED XRef Repair")
        self.resize(1400, 900)

        self._create_ui()

    def _create_ui(self) -> None:

        self.setStyleSheet("""
            QGroupBox {
                border: 1px solid #808080;
                border-radius: 3px;
                margin-top: 8px;
                font-weight: bold;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding-left: 4px;
                padding-right: 4px;
            }
        """)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(6)

        #
        # Toolbarbereich
        #

        button_layout = QHBoxLayout()

        self.open_button = QPushButton("📂 Öffnen")
        self.analyze_button = QPushButton("🔍 Analysieren")
        self.repair_button = QPushButton("🛠 Reparieren")
        self.save_button = QPushButton("💾 Speichern...")
        self.info_button = QPushButton("ℹ Info")
        self.exit_button = QPushButton("❌ Ende")

        for button in (
            self.open_button,
            self.analyze_button,
            self.repair_button,
            self.save_button,
            self.info_button,
            self.exit_button,
        ):
            button.setMinimumHeight(36)

        self.analyze_button.setEnabled(False)
        self.repair_button.setEnabled(False)
        self.save_button.setEnabled(False)

        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.analyze_button)
        button_layout.addWidget(self.repair_button)
        button_layout.addWidget(self.save_button)

        button_layout.addStretch()

        button_layout.addWidget(self.info_button)
        button_layout.addWidget(self.exit_button)

        main_layout.addLayout(button_layout)

        #
        # Dateibereich
        #

        file_group = QGroupBox("Ausgewählte GEDCOM-Datei")

        file_layout = QVBoxLayout()
        file_layout.setContentsMargins(8, 8, 8, 8)

        file_row1 = QHBoxLayout()

        file_title = QLabel("Datei:")
        file_title.setStyleSheet(
            "font-size: 11pt; font-weight: bold;"
        )

        self.filename_label = QLabel(
            "keine Datei ausgewählt"
        )

        self.filename_label.setStyleSheet(
            "font-size: 11pt;"
        )

        file_row1.addWidget(file_title)
        file_row1.addWidget(self.filename_label)
        file_row1.addStretch()

        file_row2 = QHBoxLayout()

        path_title = QLabel("Pfad:")
        path_title.setStyleSheet(
            "font-size: 11pt; font-weight: bold;"
        )

        self.path_label = QLabel("-")

        self.path_label.setStyleSheet(
            "font-size: 11pt;"
        )

        file_row2.addWidget(path_title)
        file_row2.addWidget(self.path_label)
        file_row2.addStretch()

        file_layout.addLayout(file_row1)
        file_layout.addLayout(file_row2)

        file_group.setLayout(file_layout)

        main_layout.addWidget(
            file_group,
            stretch=0
        )

        #
        # Analyseergebnis
        #

        stats_group = QGroupBox("Analyseergebnis")

        stats_layout = QGridLayout()

        #
        # Überschriften
        #

        headers = [
            "Personen",
            "Familien",
            "Datensätze",
            "Probleme"
        ]

        for col, text in enumerate(headers):

            label = QLabel(text)

            label.setAlignment(
                Qt.AlignCenter
            )

            label.setStyleSheet(
                """
                font-size: 10pt;
                font-weight: bold;
                """
            )

            stats_layout.addWidget(
                label,
                0,
                col
            )

        #
        # Werte
        #

        self.persons_value = QLabel("-")
        self.families_value = QLabel("-")
        self.records_value = QLabel("-")
        self.issues_value = QLabel("-")

        for col, label in enumerate([
            self.persons_value,
            self.families_value,
            self.records_value,
            self.issues_value,
        ]):

            label.setAlignment(
                Qt.AlignCenter
            )

            label.setStyleSheet(
                """
                font-size: 14pt;
                font-weight: bold;
                """
            )

            stats_layout.addWidget(
                label,
                1,
                col
            )

        stats_group.setLayout(
            stats_layout
        )

        main_layout.addWidget(
            stats_group,
            stretch=0
        )

        #
        # Arbeitsbereich
        #

        splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        #
        # Problemliste
        #

        problem_group = QGroupBox(
            "Problemliste"
        )

        problem_layout = QVBoxLayout()

        self.issue_table = QTableWidget()

        self.issue_table.setColumnCount(5)

        self.issue_table.setHorizontalHeaderLabels(
            [
                "","Typ",
                "Datensatz",
                "Reparierbar",
                "Beschreibung",
            ]
        )

        self.issue_table.setAlternatingRowColors(True)

        self.issue_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.issue_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        header = self.issue_table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.Stretch
        )

        selection_layout = QHBoxLayout()

        self.select_all_button = QPushButton(
            "☑ Alle auswählen"
        )

        self.clear_all_button = QPushButton(
            "☐ Keine auswählen"
        )

        self.selected_count_label = QLabel(
            "Ausgewählt: 0"
        )

        selection_layout.addWidget(
            self.select_all_button
        )

        selection_layout.addWidget(
            self.clear_all_button
        )

        selection_layout.addStretch()

        selection_layout.addWidget(
            self.selected_count_label
        )

        problem_layout.addLayout(
            selection_layout
        )
        
        problem_layout.addWidget(
            self.issue_table
        )

        problem_group.setLayout(
            problem_layout
        )

        #
        # Detailansicht
        #

        detail_group = QGroupBox(
            "Details"
        )

        detail_layout = QVBoxLayout()

        self.detail_placeholder = QLabel(
            "Hier erscheinen später Detailinformationen"
        )

        self.detail_placeholder.setAlignment(
            Qt.AlignCenter
        )

        self.detail_placeholder.setStyleSheet(
            """
            font-size: 12pt;
            color: gray;
            """
        )

        detail_layout.addWidget(
            self.detail_placeholder
        )

        detail_group.setLayout(
            detail_layout
        )

        splitter.addWidget(
            problem_group
        )

        splitter.addWidget(
            detail_group
        )

        #
        # 70 / 30 Verteilung
        #

        splitter.setSizes(
            [700, 300]
        )

        #
        # Hauptfläche erhält fast die gesamte Höhe
        #

        main_layout.addWidget(
            splitter,
            stretch=10
        )

        #
        # Events
        #

        self.open_button.clicked.connect(
            self.select_file
        )

        self.analyze_button.clicked.connect(
            self.start_analysis
        )

        self.info_button.clicked.connect(
            self.show_info
        )

        self.exit_button.clicked.connect(
            self.close
        )

        self.statusBar().showMessage(
            "Bereit"
        )
        
        self.select_all_button.clicked.connect(
            self.select_all_issues
        )

        self.clear_all_button.clicked.connect(
            self.clear_all_issues
        )
        
        self.issue_table.itemChanged.connect(
            self.on_issue_item_changed
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

        path = Path(filename)

        self.filename_label.setText(
            path.name
        )

        self.path_label.setText(
            str(path.parent)
        )

        self.analyze_button.setEnabled(True)

        self.statusBar().showMessage(
            "Datei geladen"
        )

    def start_analysis(self) -> None:

        if not self.gedcom_file:
            return

        service = AnalysisService()

        result = service.analyze(
            self.gedcom_file
        )

        self.persons_value.setText(
            str(result.individuals)
        )

        self.families_value.setText(
            str(result.families)
        )

        self.records_value.setText(
            str(result.records)
        )

        self.issues_value.setText(
            str(result.issues_count)
        )

        self.populate_issue_table(
            result.issues
        )

        self.statusBar().showMessage(
            "Analyse abgeschlossen"
        )        

    def populate_issue_table(
        self,
        issues
    ) -> None:

        self.issue_table.setRowCount(len(issues))

        for row, issue in enumerate(issues):

            checkbox_item = QTableWidgetItem()

            checkbox_item.setFlags(
                checkbox_item.flags()
                | Qt.ItemFlag.ItemIsUserCheckable
            )

            checkbox_item.setCheckState(
                Qt.CheckState.Checked
                if issue.auto_repair_possible
                else Qt.CheckState.Unchecked
            )

            self.issue_table.setItem(
                row,
                0,
                checkbox_item
            )

            self.issue_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    issue.issue_type
                )
            )

            self.issue_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    issue.record_id
                )
            )

            self.issue_table.setItem(
                row,
                3,
                QTableWidgetItem(
                    "Ja"
                    if issue.auto_repair_possible
                    else "Nein"
                )
            )

            self.issue_table.setItem(
                row,
                4,
                QTableWidgetItem(
                    issue.description
                )
            )
            
        self.update_selected_count()
            

    def select_all_issues(self) -> None:

        for row in range(
            self.issue_table.rowCount()
        ):

            item = self.issue_table.item(
                row,
                0
            )

            if item is not None:

                item.setCheckState(
                    Qt.CheckState.Checked
                )

        self.update_selected_count()

    def clear_all_issues(self) -> None:

        for row in range(
            self.issue_table.rowCount()
        ):

            item = self.issue_table.item(
                row,
                0
            )

            if item is not None:

                item.setCheckState(
                    Qt.CheckState.Unchecked
                )

        self.update_selected_count()
        
    def update_selected_count(self) -> None:

        selected = 0

        for row in range(
            self.issue_table.rowCount()
        ):

            item = self.issue_table.item(
                row,
                0
            )

            if (
                item is not None
                and item.checkState()
                == Qt.CheckState.Checked
            ):
                selected += 1

        self.selected_count_label.setText(
            f"Ausgewählt: {selected}"
        )        
        
    def on_issue_item_changed(
        self,
        item
    ) -> None:

        if item.column() == 0:
            self.update_selected_count()

    def show_info(self) -> None:

        QMessageBox.information(
            self,
            "Info",
            (
                "GED XRef Repair\n\n"
                "Werkzeug zur Analyse und Reparatur\n"
                "von GEDCOM-Referenzen."
            )
        )