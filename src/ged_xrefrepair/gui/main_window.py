# src/ged_xrefrepair/gui/main_window.py

from copy import deepcopy
from html import escape
from pathlib import Path
import shutil

from PySide6.QtCore import (
    Qt,
    QTimer,
    QSettings,
    QThread,
)

from PySide6.QtGui import QCloseEvent

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
    QTextEdit,
    QAbstractItemView,
    QComboBox,
)

from ged_xrefrepair import __version__
from ged_xrefrepair.analyzer.reference_analyzer import ReferenceAnalyzer
from ged_xrefrepair.gui.analysis_worker import AnalysisWorker
from ged_xrefrepair.gui.problem_overview_window import (
    ProblemOverviewWindow,
)
from ged_xrefrepair.gui.repair_log_window import RepairLogWindow
from ged_xrefrepair.services.name_resolver import NameResolver
from ged_xrefrepair.analyzer.analysis_result import AnalysisResult
from ged_xrefrepair.services.repair_preview_service import (
    RepairPreviewService
)
from ged_xrefrepair.services.repair_service import RepairService
from ged_xrefrepair.parser.gedcom_writer import GedcomWriter
from ged_xrefrepair.model.issue import Issue, RepairStatus
from ged_xrefrepair.services.repair_log_writer import RepairLogWriter


class MainWindow(QMainWindow):
    ISSUE_EXPLANATIONS = {
        "MISSING_CHIL": (
            "Fehlender Kind-Verweis in der Familie",
            (
                "Die ausgewählte Person verweist über einen FAMC-Eintrag "
                "auf diese Familie.",
                "Im Familiendatensatz fehlt jedoch der zugehörige "
                "CHIL-Eintrag, der die Person als Kind dieser Familie "
                "aufführt.",
                "Dadurch ist die Eltern-Kind-Beziehung nur in einer "
                "Richtung definiert. Genealogische Programme können diese "
                "Beziehung deshalb möglicherweise nicht vollständig "
                "auswerten.",
            ),
        ),
        "MISSING_FAMC": (
            "Fehlender Familien-Verweis bei einer Person",
            (
                "Die Familie enthält diese Person als Kind (CHIL).",
                "Im Personendatensatz fehlt jedoch der entsprechende "
                "FAMC-Eintrag, der auf die Familie verweist.",
                "Dadurch ist die Eltern-Kind-Beziehung nur in einer "
                "Richtung definiert. Die Zuordnung zu den Eltern kann "
                "deshalb unvollständig dargestellt werden.",
            ),
        ),
        "MISSING_HUSB": (
            "Fehlender Ehemann-Eintrag in der Familie",
            (
                "Eine Person verweist über einen FAMS-Eintrag auf diese "
                "Familie.",
                "Im Familiendatensatz fehlt jedoch der zugehörige "
                "HUSB-Eintrag.",
                "Dadurch ist die Ehe- bzw. Partnerschaftsbeziehung nicht "
                "vollständig definiert. Die Familie kennt den Ehemann "
                "nicht, obwohl die Person auf die Familie verweist.",
            ),
        ),
        "MISSING_WIFE": (
            "Fehlender Ehefrau-Eintrag in der Familie",
            (
                "Eine Person verweist über einen FAMS-Eintrag auf diese "
                "Familie.",
                "Im Familiendatensatz fehlt jedoch der zugehörige "
                "WIFE-Eintrag.",
                "Dadurch ist die Ehe- bzw. Partnerschaftsbeziehung nicht "
                "vollständig definiert. Die Familie kennt die Ehefrau "
                "nicht, obwohl die Person auf die Familie verweist.",
            ),
        ),
        "MISSING_FAMS_HUSB": (
            "Fehlender Familien-Verweis beim Ehemann",
            (
                "Die Familie enthält diese Person als HUSB.",
                "Im Personendatensatz fehlt jedoch der entsprechende "
                "FAMS-Eintrag, der auf die Familie verweist.",
                "Dadurch ist die Partnerschaftsbeziehung nur in einer "
                "Richtung erfasst. Einige Genealogieprogramme können die "
                "Zugehörigkeit zur Familie deshalb nicht vollständig "
                "darstellen.",
            ),
        ),
        "MISSING_FAMS_WIFE": (
            "Fehlender Familien-Verweis bei der Ehefrau",
            (
                "Die Familie enthält diese Person als WIFE.",
                "Im Personendatensatz fehlt jedoch der entsprechende "
                "FAMS-Eintrag, der auf die Familie verweist.",
                "Dadurch ist die Partnerschaftsbeziehung nur in einer "
                "Richtung erfasst. Einige Genealogieprogramme können die "
                "Zugehörigkeit zur Familie deshalb nicht vollständig "
                "darstellen.",
            ),
        ),
        "MISSING_PERSON": (
            "Verweis auf eine nicht vorhandene Person",
            (
                "Ein Familiendatensatz verweist auf eine Person, die in "
                "der GEDCOM-Datei nicht existiert.",
                "Der betreffende Verweis kann daher nicht aufgelöst "
                "werden.",
                "Mögliche Ursachen sind ein gelöschter Personendatensatz, "
                "eine falsche XRef-ID oder eine beschädigte GEDCOM-Datei.",
                "Eine automatische Reparatur ist nicht möglich, da nicht "
                "eindeutig bestimmt werden kann, auf welche Person "
                "verwiesen werden sollte.",
            ),
        ),
        "MISSING_FAMILY": (
            "Verweis auf eine nicht vorhandene Familie",
            (
                "Ein Personen- oder Familiendatensatz verweist auf eine "
                "Familie, die in der GEDCOM-Datei nicht existiert.",
                "Der betreffende Verweis kann daher nicht aufgelöst "
                "werden.",
                "Mögliche Ursachen sind ein gelöschter Familiendatensatz, "
                "eine falsche XRef-ID oder eine beschädigte GEDCOM-Datei.",
                "Eine automatische Reparatur ist nicht möglich, da nicht "
                "eindeutig bestimmt werden kann, welche Familie gemeint "
                "war.",
            ),
        ),
    }

    ISSUE_RECORD_ORDER = {
        "MISSING_CHIL": (("Person", "related"), ("Familie", "record")),
        "MISSING_FAMC": (("Person", "record"), ("Familie", "related")),
        "MISSING_HUSB": (("Person", "related"), ("Familie", "record")),
        "MISSING_WIFE": (("Person", "related"), ("Familie", "record")),
        "MISSING_FAMS_HUSB": (("Person", "record"), ("Familie", "related")),
        "MISSING_FAMS_WIFE": (("Person", "record"), ("Familie", "related")),
        "MISSING_PERSON": (("Familie", "record"), ("Person", "related")),
        "MISSING_FAMILY": (("Datensatz", "record"), ("Familie", "related")),
    }

    def __init__(self) -> None:
        super().__init__()

        self.settings = QSettings(
            "ged-xrefrepair",
            "GED XRef Repair"
        )
        
        self.gedcom_file = None
        self.current_issues = []
        self.current_records = []
        self.name_resolver = None
        self._has_unsaved_repairs = False
        self.repair_service = RepairService()
        self._repair_status_history: dict[
            tuple[str, str, str], Issue
        ] = {}
        self._repair_ui_undo_stack: list[
            tuple[dict[tuple[str, str, str], Issue], bool]
        ] = []
        self._repair_log_path: Path | None = None
        self.repair_log_window: RepairLogWindow | None = None
        self._analysis_thread: QThread | None = None
        self._analysis_worker: AnalysisWorker | None = None
        self._analysis_in_progress = False
        self._analysis_thread_done = False
        self._analysis_display_done = False
        self._analysis_final_message = ""
        self.problem_overview_window: ProblemOverviewWindow | None = None
        
        self.setWindowTitle(f"GED XRef Repair v.{__version__}")
        self.resize(1400, 900)

        self._create_ui()
        
        self.restore_last_file()
     

    def _create_ui(self) -> None:

        # Fensterstil
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
        # Setze das zentrale Widget des Hauptfensters
        self.setCentralWidget(central)

        # Hauptlayout
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(6)

        #
        # Toolbarbereich
        #

        button_layout = QHBoxLayout()

        self.open_button = QPushButton("📂 Öffnen")
        self.analyze_button = QPushButton("🔍 Analysieren")
        self.repair_button = QPushButton("🛠 Reparieren")
        self.undo_button = QPushButton("↶ Rückgängig")
        self.save_button = QPushButton("💾 Speichern...")
        self.repair_log_button = QPushButton("📋 Protokoll")
        self.help_button = QPushButton("❓ HILFE")
        self.info_button = QPushButton("ℹ Info")
        self.exit_button = QPushButton("❌ Ende")

        for button in (
            self.open_button,
            self.analyze_button,
            self.repair_button,
            self.undo_button,
            self.save_button,
            self.repair_log_button,
            self.help_button,
            self.info_button,
            self.exit_button,
        ):
            button.setMinimumHeight(36)

        self.analyze_button.setEnabled(False)
        self.repair_button.setEnabled(False)
        self.undo_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.repair_log_button.setEnabled(False)

        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.analyze_button)
        button_layout.addWidget(self.repair_button)
        button_layout.addWidget(self.undo_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.repair_log_button)

        button_layout.addStretch()

        button_layout.addWidget(self.help_button)
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

        self.issue_type_filter = QComboBox()
        self.issue_type_filter.addItem("Alle Typen", None)
        self.repairability_filter = QComboBox()
        self.repairability_filter.addItem("Alle", None)
        self.repairability_filter.addItem("Reparierbar", True)
        self.repairability_filter.addItem("Nicht reparierbar", False)

        self.issue_table = QTableWidget()

        self.issue_table.setColumnCount(6)
        
        self.issue_table.setSortingEnabled(True)

        self.issue_table.setHorizontalHeaderLabels(
            [
                "",
                "Datensatz",
                "Problemfall",
                "Typ",
                "Reparierbar",
                "Status",
            ]
        )
        
        self.issue_table.setColumnWidth(0, 40)   # Checkbox
        self.issue_table.setColumnWidth(1, 100)  # Datensatz
        self.issue_table.setColumnWidth(2, 300)  # Problemfall
        self.issue_table.setColumnWidth(3, 120)  # Typ
        self.issue_table.setColumnWidth(4, 100)  # Reparierbar
        self.issue_table.setColumnWidth(5, 65)   # Status

        self.issue_table.setAlternatingRowColors(True)

        self.issue_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.issue_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.issue_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        header = self.issue_table.horizontalHeader()
        
        header.sortIndicatorChanged.connect(
           self.on_table_sorted
        )
        
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
            QHeaderView.ResizeMode.Interactive
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            5,
            QHeaderView.ResizeMode.ResizeToContents
        )

        selection_layout = QHBoxLayout()

        self.select_all_button = QPushButton(
            "☑ Alle auswählen"
        )

        self.clear_all_button = QPushButton(
            "☐ Keine auswählen"
        )
        
        self.invert_selection_button = QPushButton(
            "⇄ Auswahl umkehren"
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
        
        selection_layout.addWidget(
            self.invert_selection_button
        )

        selection_layout.addWidget(
            self.selected_count_label
        )

        selection_layout.addStretch()
        selection_layout.addWidget(QLabel("Typ:"))
        selection_layout.addWidget(self.issue_type_filter)
        selection_layout.addWidget(QLabel("Reparierbarkeit:"))
        selection_layout.addWidget(self.repairability_filter)

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

        self.detail_view = QTextEdit()
        self.detail_view.setReadOnly(True)

        detail_layout.addWidget(
            self.detail_view
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

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

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

        self.help_button.clicked.connect(
            self.show_problem_overview
        )

        self.repair_button.clicked.connect(
            self.apply_selected_repairs
        )

        self.undo_button.clicked.connect(
            self.undo_last_repair
        )

        self.save_button.clicked.connect(
            self.save_repaired_file
        )

        self.repair_log_button.clicked.connect(
            self.show_repair_log
        )

        # Wenn der "Ende"-Button geklickt wird, soll das Programm beendet werden
        self.exit_button.clicked.connect(
            self.close
        )

        self.statusBar().showMessage(
            "Bereit"
        )

        # Wenn der "Alle auswählen"-Button geklickt wird, sollen alle Probleme ausgewählt werden
        self.select_all_button.clicked.connect(
            self.select_all_issues
        )
 
        # Wenn der "Auswahl umkehren"-Button geklickt wird, sollen die ausgewählten Probleme abgewählt und die abgewählten Probleme ausgewählt werden       
        self.invert_selection_button.clicked.connect(
            self.invert_selection
        )

        # Wenn der "Keine auswählen"-Button geklickt wird, sollen alle Probleme abgewählt werden
        self.clear_all_button.clicked.connect(
            self.clear_all_issues
        )
        
        # Wenn ein Item in der Tabelle geändert wird, soll die Anzahl der ausgewählten Probleme aktualisiert werden
        self.issue_table.itemChanged.connect(
            self.on_issue_item_changed
        )
        
        # Wenn die Auswahl in der Tabelle geändert wird, sollen die Details angezeigt werden
        self.issue_table.itemSelectionChanged.connect(
            self.show_issue_details
        )

        self.issue_type_filter.currentIndexChanged.connect(
            self.apply_issue_filters
        )
        self.repairability_filter.currentIndexChanged.connect(
            self.apply_issue_filters
        )

    def select_file(self) -> None:

        last_file = self.settings.value(
            "last_file",
            "",
            str
        )

        start_dir = ""

        if last_file:

            last_path = Path(last_file)

            if last_path.exists():

                start_dir = str(
                    last_path.parent
                )
                
        else:
            start_dir = str(
                Path.home()
            )

        self.path_label.setText(
            start_dir
        )

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "GEDCOM-Datei auswählen",
            start_dir,
            "GEDCOM Dateien (*.ged *.gedcom)"
        )

        if not filename:
            return

        self._repair_status_history.clear()
        self._repair_ui_undo_stack.clear()
        self._repair_log_path = None
        self.repair_log_button.setEnabled(False)
        self.gedcom_file = filename

        self.settings.setValue(
            "last_file",
            filename
        )

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

        #
        # Bei bewusstem Öffnen durch den Benutzer
        # soll die Analyse sofort starten
        #

        self.start_analysis()
    
    def start_analysis(self) -> None:

        if not self.gedcom_file or self._analysis_in_progress:
            return

        self._analysis_in_progress = True
        self._analysis_thread_done = False
        self._analysis_display_done = False
        self._analysis_final_message = ""
        self._clear_analysis_results()
        self.open_button.setEnabled(False)
        self.analyze_button.setEnabled(False)
        self.statusBar().showMessage("Analyse läuft...")

        self._analysis_thread = QThread(self)
        self._analysis_worker = AnalysisWorker(self.gedcom_file)
        self._analysis_worker.moveToThread(self._analysis_thread)
        self._analysis_thread.started.connect(
            self._analysis_worker.run
        )
        self._analysis_worker.result_ready.connect(
            self._on_analysis_completed
        )
        self._analysis_worker.failed.connect(
            self._on_analysis_failed
        )
        self._analysis_worker.finished.connect(
            self._analysis_thread.quit
        )
        self._analysis_thread.finished.connect(
            self._analysis_worker.deleteLater
        )
        self._analysis_thread.finished.connect(
            self._on_analysis_thread_finished
        )
        self._analysis_thread.finished.connect(
            self._analysis_thread.deleteLater
        )
        self._analysis_thread.start()

    def _on_analysis_completed(
        self,
        result: AnalysisResult,
    ) -> None:
        # Aktuelle Probleme speichern
        self.current_issues = self._merge_repair_statuses(result.issues)
        self.current_records = result.record_list
        self._has_unsaved_repairs = False
        self.repair_service.clear_undo()
        
        # NameResolver initialisieren, um die XRef-IDs in lesbare Namen aufzulösen
        self.name_resolver = NameResolver(
            result.record_list
        )

        # Ergebnisse in der GUI anzeigen
        self.persons_value.setText(
            str(result.individuals)
        )

        # Familienanzahl anzeigen
        self.families_value.setText(
            str(result.families)
        )

        # Datensatzanzahl anzeigen
        self.records_value.setText(
            str(result.records)
        )

        # Probleme anzeigen
        self.issues_value.setText(
            str(result.issues_count)
        )

        self._analysis_final_message = "Analyse abgeschlossen"
        self._start_issue_table_population(self.current_issues)

    def _on_analysis_failed(self, error: Exception) -> None:
        self._analysis_final_message = "Analyse fehlgeschlagen"

        if isinstance(error, UnicodeDecodeError):
            title = "Datei kann nicht gelesen werden"
            message = (
                "Die GEDCOM-Datei ist nicht als UTF-8 lesbar. "
                "Bitte prüfen Sie die Dateikodierung.\n\n"
                f"{error}"
            )
        elif isinstance(error, OSError):
            title = "Datei kann nicht gelesen werden"
            message = (
                "Die GEDCOM-Datei konnte nicht geöffnet oder gelesen "
                "werden.\n\n"
                f"{error}"
            )
        else:
            title = "Analyse fehlgeschlagen"
            message = (
                "Bei der Analyse ist ein unerwarteter Fehler aufgetreten. "
                "Details wurden protokolliert.\n\n"
                f"{error}"
            )

        QMessageBox.critical(
            self,
            title,
            message,
        )
        self._analysis_display_done = True
        self._finish_analysis_if_ready()

    def _on_analysis_thread_finished(self) -> None:
        self._analysis_worker = None
        self._analysis_thread = None
        self._analysis_thread_done = True
        self._finish_analysis_if_ready()

    def _finish_analysis_if_ready(self) -> None:
        if not (
            self._analysis_thread_done
            and self._analysis_display_done
        ):
            return

        self._analysis_in_progress = False
        self.open_button.setEnabled(True)
        self.analyze_button.setEnabled(
            self.gedcom_file is not None
        )
        self.statusBar().showMessage(
            self._analysis_final_message
        )

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._analysis_in_progress:
            event.ignore()
            return

        if self.problem_overview_window is not None:
            self.problem_overview_window.close()
        if self.repair_log_window is not None:
            self.repair_log_window.close()

        event.accept()

    def _clear_analysis_results(self) -> None:
        self.current_issues = []
        self.current_records = []
        self.name_resolver = None
        self._has_unsaved_repairs = False
        self.repair_service.clear_undo()
        self._repair_ui_undo_stack.clear()

        self.persons_value.setText("-")
        self.families_value.setText("-")
        self.records_value.setText("-")
        self.issues_value.setText("-")

        self.issue_table.setRowCount(0)
        self.issue_type_filter.clear()
        self.issue_type_filter.addItem("Alle Typen", None)
        self.repairability_filter.setCurrentIndex(0)
        self.detail_view.clear()
        self.selected_count_label.setText("Ausgewählt: 0")

        self.repair_button.setEnabled(False)
        self.undo_button.setEnabled(False)
        self.save_button.setEnabled(False)

    def populate_issue_table(
        self,
        issues
    ) -> None:
        self._start_issue_table_population(issues)

    @staticmethod
    def _issue_status_key(issue: Issue) -> tuple[str, str, str]:
        return (issue.issue_type, issue.record_id, issue.related_xref)

    @staticmethod
    def _repair_status_symbol(issue: Issue) -> str:
        if not issue.auto_repair_possible:
            return "—"
        symbols: dict[RepairStatus, str] = {
            "NOT_PROCESSED": "",
            "REPAIRED": "✅",
            "SKIPPED": "⚠",
            "FAILED": "❌",
        }
        return symbols[issue.repair_status]

    @staticmethod
    def _repair_status_tooltip(issue: Issue) -> str:
        if not issue.auto_repair_possible:
            return "Keine automatische Reparatur möglich"
        tooltips: dict[RepairStatus, str] = {
            "NOT_PROCESSED": "Noch nicht bearbeitet",
            "REPAIRED": "Reparatur erfolgreich durchgeführt",
            "SKIPPED": "Keine Änderung erforderlich",
            "FAILED": "Reparaturversuch fehlgeschlagen",
        }
        return tooltips[issue.repair_status]

    def _remember_repair_statuses(self, issues: list[Issue]) -> None:
        for issue in issues:
            self._repair_status_history[self._issue_status_key(issue)] = (
                deepcopy(issue)
            )

    def _merge_repair_statuses(self, issues: list[Issue]) -> list[Issue]:
        displayed_issues = list(issues)
        current_keys = {
            self._issue_status_key(issue)
            for issue in displayed_issues
        }

        for issue in displayed_issues:
            previous = self._repair_status_history.get(
                self._issue_status_key(issue)
            )
            if previous is not None:
                issue.repair_status = previous.repair_status

        for key, previous in self._repair_status_history.items():
            if (
                key not in current_keys
                and previous.repair_status != "NOT_PROCESSED"
            ):
                displayed_issues.append(deepcopy(previous))

        return displayed_issues

    def _start_issue_table_population(self, issues) -> None:
        issue_types = sorted({issue.issue_type for issue in issues})
        self.issue_type_filter.blockSignals(True)
        self.issue_type_filter.clear()
        self.issue_type_filter.addItem("Alle Typen", None)
        for issue_type in issue_types:
            self.issue_type_filter.addItem(issue_type, issue_type)
        self.issue_type_filter.blockSignals(False)
        self.repairability_filter.setCurrentIndex(0)

        self.issue_table.setSortingEnabled(False)
        self.issue_table.setRowCount(len(issues))
        for row, issue in enumerate(issues):
            checkbox_item = QTableWidgetItem()
            checkbox_item.setData(
                Qt.ItemDataRole.UserRole,
                issue
            )
            checkbox_item.setFlags(
                checkbox_item.flags()
                | (
                    Qt.ItemFlag.ItemIsUserCheckable
                    if issue.repair_status
                    not in ("REPAIRED", "SKIPPED")
                    else Qt.ItemFlag(0)
                )
            )
            checkbox_item.setCheckState(Qt.CheckState.Unchecked)
            self.issue_table.setItem(
                row,
                0,
                checkbox_item
            )
            self.issue_table.setItem(
                row,
                1,
                QTableWidgetItem(issue.record_id)
            )
            self.issue_table.setItem(
                row,
                2,
                QTableWidgetItem(issue.description)
            )
            self.issue_table.setItem(
                row,
                3,
                QTableWidgetItem(issue.issue_type)
            )
            self.issue_table.setItem(
                row,
                4,
                QTableWidgetItem(
                    "Ja" if issue.auto_repair_possible else "Nein"
                )
            )
            status_item = QTableWidgetItem(
                self._repair_status_symbol(issue)
            )
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setToolTip(self._repair_status_tooltip(issue))
            self.issue_table.setItem(row, 5, status_item)

        self.update_selected_count()
        self.apply_issue_filters()
        self.detail_view.clear()
        self.issue_table.setSortingEnabled(True)
        self._analysis_display_done = True
        self._finish_analysis_if_ready()

    def select_all_issues(self) -> None:

        for row in range(
            self.issue_table.rowCount()
        ):

            if self.issue_table.isRowHidden(row):
                continue

            item = self.issue_table.item(
                row,
                0
            )

            if item is not None:
                if not item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                    continue

                item.setCheckState(
                    Qt.CheckState.Checked
                )

        self.update_selected_count()

    def clear_all_issues(self) -> None:

        for row in range(
            self.issue_table.rowCount()
        ):

            if self.issue_table.isRowHidden(row):
                continue

            item = self.issue_table.item(
                row,
                0
            )

            if item is not None:
                if not item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                    continue

                item.setCheckState(
                    Qt.CheckState.Unchecked
                )

        self.update_selected_count()
        
    def invert_selection(self) -> None:

        self.issue_table.blockSignals(True)

        for row in range(
            self.issue_table.rowCount()
        ):

            if self.issue_table.isRowHidden(row):
                continue

            item = self.issue_table.item(
                row,
                0
            )

            if item is None:
                continue
            if not item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                continue

            if (
                item.checkState()
                == Qt.CheckState.Checked
            ):

                item.setCheckState(
                    Qt.CheckState.Unchecked
                )

            else:

                item.setCheckState(
                    Qt.CheckState.Checked
                )

        self.issue_table.blockSignals(False)

        self.update_selected_count()

    def apply_issue_filters(self, *args) -> None:
        selected_type = self.issue_type_filter.currentData()
        selected_repairability = self.repairability_filter.currentData()

        for row in range(self.issue_table.rowCount()):
            item = self.issue_table.item(row, 0)
            issue = (
                item.data(Qt.ItemDataRole.UserRole)
                if item is not None
                else None
            )
            matches_type = (
                selected_type is None
                or (
                    issue is not None
                    and issue.issue_type == selected_type
                )
            )
            matches_repairability = (
                selected_repairability is None
                or (
                    issue is not None
                    and issue.auto_repair_possible
                    is selected_repairability
                )
            )
            self.issue_table.setRowHidden(
                row,
                not (matches_type and matches_repairability),
            )
    
            
    def update_selected_count(self) -> None:

        selected = 0
        selected_repairable = False

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
                issue = item.data(Qt.ItemDataRole.UserRole)
                if (
                    issue is not None
                    and issue.auto_repair_possible
                    and issue.repair_status not in ("REPAIRED", "SKIPPED")
                ):
                    selected_repairable = True

        self.selected_count_label.setText(
            f"Ausgewählt: {selected}"
        )
        self.repair_button.setEnabled(
            bool(self.current_records) and selected_repairable
        )
        self.undo_button.setEnabled(self.repair_service.can_undo)
        self.save_button.setEnabled(self._has_unsaved_repairs)

    def apply_selected_repairs(self) -> None:
        selected_issues = []
        for row in range(self.issue_table.rowCount()):
            item = self.issue_table.item(row, 0)
            if (
                item is not None
                and item.checkState() == Qt.CheckState.Checked
            ):
                issue = item.data(Qt.ItemDataRole.UserRole)
                if issue is not None:
                    selected_issues.append(issue)

        actionable_issues = [
            issue
            for issue in selected_issues
            if issue.auto_repair_possible
            and issue.repair_status not in ("REPAIRED", "SKIPPED")
        ]
        if not actionable_issues:
            return

        confirmation = QMessageBox.question(
            self,
            "Reparatur bestätigen",
            (
                f"{len(actionable_issues)} "
                f"{'Problem wird' if len(actionable_issues) == 1 else 'Probleme werden'} "
                "jetzt korrigiert. Möchten Sie fortfahren?"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return

        self._repair_ui_undo_stack.append(
            (deepcopy(self._repair_status_history), self._has_unsaved_repairs)
        )
        try:
            self.current_records = self.repair_service.apply_selected(
                self.current_records,
                actionable_issues,
            )
        except Exception as error:
            self._repair_ui_undo_stack.pop()
            QMessageBox.critical(
                self,
                "Reparatur fehlgeschlagen",
                str(error),
            )
            return

        self._remember_repair_statuses(actionable_issues)
        if self.repair_service.last_changed_count and self.gedcom_file:
            try:
                self._repair_log_path = RepairLogWriter().append_run(
                    self.gedcom_file,
                    actionable_issues,
                )
                self.repair_log_button.setEnabled(
                    self._repair_log_path is not None
                )
            except OSError as error:
                existing_log = Path(
                    f"{self.gedcom_file}.repair.log"
                )
                self._repair_log_path = (
                    existing_log if existing_log.is_file() else None
                )
                self.repair_log_button.setEnabled(
                    self._repair_log_path is not None
                )
                QMessageBox.warning(
                    self,
                    "Protokoll konnte nicht gespeichert werden",
                    f"Die Reparaturen wurden durchgeführt, aber das "
                    f"Protokoll konnte nicht geschrieben werden.\n\n{error}",
                )
        if self.repair_service.last_changed_count:
            self._has_unsaved_repairs = True
        self._refresh_analysis_from_current_records()
        self.statusBar().showMessage(
            "Reparatur abgeschlossen: "
            f"{self.repair_service.last_changed_count} "
            f"{'Reparatur' if self.repair_service.last_changed_count == 1 else 'Reparaturen'} "
            "durchgeführt, "
            f"{self.repair_service.last_skipped_count} "
            f"{'Reparatur' if self.repair_service.last_skipped_count == 1 else 'Reparaturen'} "
            "übersprungen, "
            f"{self.repair_service.last_failed_count} "
            f"{'Fehler' if self.repair_service.last_failed_count != 1 else 'Fehler'}"
            ". Weiter mit Speichern"
        )

    def undo_last_repair(self) -> None:
        if not self.repair_service.can_undo:
            return

        self.current_records = self.repair_service.undo(
            self.current_records
        )
        if self._repair_ui_undo_stack:
            (
                self._repair_status_history,
                self._has_unsaved_repairs,
            ) = self._repair_ui_undo_stack.pop()
        self._refresh_analysis_from_current_records()
        self.statusBar().showMessage("Änderungen rückgängig gemacht")

    def _refresh_analysis_from_current_records(self) -> None:
        issues = ReferenceAnalyzer().analyze(self.current_records)
        individuals = sum(
            record.tag == "INDI"
            for record in self.current_records
        )
        families = sum(
            record.tag == "FAM"
            for record in self.current_records
        )
        self.current_issues = self._merge_repair_statuses(issues)
        self.name_resolver = NameResolver(self.current_records)
        self.persons_value.setText(str(individuals))
        self.families_value.setText(str(families))
        self.records_value.setText(str(len(self.current_records)))
        self.issues_value.setText(str(len(issues)))
        self._start_issue_table_population(self.current_issues)

    def save_repaired_file(self) -> None:
        if not self._has_unsaved_repairs or not self.gedcom_file:
            return

        source_path = Path(self.gedcom_file)
        default_path = source_path.with_name(
            f"{source_path.stem}_repaired{source_path.suffix}"
        )
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Reparierte GEDCOM-Datei speichern",
            str(default_path),
            "GEDCOM Dateien (*.ged *.gedcom)",
        )
        if not filename:
            return

        output_path = Path(filename).resolve()
        backup_path = Path(f"{source_path}.bak").resolve()
        if output_path == source_path.resolve():
            QMessageBox.warning(
                self,
                "Originaldatei schützen",
                "Die Originaldatei wird nicht überschrieben. "
                "Bitte wählen Sie einen anderen Dateinamen.",
            )
            return
        if output_path == backup_path:
            QMessageBox.warning(
                self,
                "Sicherung schützen",
                "Der ausgewählte Dateiname ist für die automatische "
                "Sicherung reserviert. Bitte wählen Sie einen anderen Namen.",
            )
            return
        if output_path.exists():
            overwrite = QMessageBox.question(
                self,
                "Datei überschreiben?",
                f"Die Datei {output_path.name} existiert bereits. "
                "Soll sie ersetzt werden?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if overwrite != QMessageBox.StandardButton.Yes:
                return

        writer = GedcomWriter()
        try:
            backup_path = writer.create_backup(source_path)
            self.statusBar().showMessage(
                f"Sicherung erstellt: {backup_path.name}"
            )
            repair_count = sum(
                issue.repair_status == "REPAIRED"
                for issue in self._repair_status_history.values()
            )
            writer.write(
                self.current_records,
                str(output_path),
                repair_count=repair_count,
            )
        except (OSError, shutil.Error) as error:
            QMessageBox.critical(
                self,
                "Speichern fehlgeschlagen",
                f"Die reparierte Datei konnte nicht gespeichert werden.\n\n"
                f"{error}",
            )
            return

        self._has_unsaved_repairs = False
        self.save_button.setEnabled(False)
        self.statusBar().showMessage("Datei gespeichert")
        
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

    def show_repair_log(self) -> None:
        if self._repair_log_path is None:
            return

        try:
            log_content = self._repair_log_path.read_text(encoding="utf-8")
        except OSError as error:
            QMessageBox.warning(
                self,
                "Protokoll kann nicht gelesen werden",
                f"Das Reparaturprotokoll konnte nicht geöffnet werden.\n\n"
                f"{error}",
            )
            return

        if self.repair_log_window is None:
            self.repair_log_window = RepairLogWindow(self, log_content)
        else:
            self.repair_log_window.text_edit.setPlainText(log_content)
        self.repair_log_window.show()
        self.repair_log_window.raise_()
        self.repair_log_window.activateWindow()

    def show_problem_overview(self) -> None:
        if self.problem_overview_window is None:
            self.problem_overview_window = ProblemOverviewWindow(
                self
            )

        self.problem_overview_window.show()
        self.problem_overview_window.raise_()
        self.problem_overview_window.activateWindow()
        
        # Wenn ein Problem in der Tabelle ausgewählt wird, sollen die Details angezeigt werden
    def show_issue_details(
        self,
        *args
    ) -> None:

        row = self.issue_table.currentRow()

        if row < 0:
            self.detail_view.clear()
            return

        item = self.issue_table.item(
            row,
            0
        )

        if item is None:
            return


        issue = item.data(
            Qt.ItemDataRole.UserRole
        )

        preview_service = RepairPreviewService()
        repair_action = preview_service.create_action(issue)

        def resolved_record(label: str, xref: str) -> str:
            resolved_name = self.name_resolver.resolve(xref)
            if resolved_name == xref:
                record_kind = (
                    "Person"
                    if xref.startswith("@I")
                    else "Familie"
                    if xref.startswith("@F")
                    else "Datensatz"
                )
                resolved_name = f"{record_kind} nicht vorhanden"

            name_html = escape(resolved_name).replace("\n", "<br>")
            return (
                f"<p><b>{escape(label)}:</b><br>"
                f"{name_html}<br>"
                f"Datensatz: <code>{escape(xref)}</code></p>"
            )

        affected_records = []
        for label, source in self.ISSUE_RECORD_ORDER.get(
            issue.issue_type,
            (("Datensatz", "record"), ("Korrespondierender Datensatz", "related")),
        ):
            xref = (
                issue.record_id
                if source == "record"
                else issue.related_xref
            )
            affected_records.append(resolved_record(label, xref))

        title, explanations = self.ISSUE_EXPLANATIONS.get(
            issue.issue_type,
            ("Unbekannter Problemtyp", (issue.description,)),
        )
        explanation_html = "".join(
            f"<p>{escape(paragraph)}</p>"
            for paragraph in explanations
        )

        if issue.repair_status == "REPAIRED":
            target_html = (
                resolved_record("Zieldatensatz", repair_action.target_record)
                if repair_action is not None
                else ""
            )
            line_html = (
                f"<p>Einzufügende Zeile:</p>"
                f"<p><code>{escape(repair_action.new_line)}</code></p>"
                if repair_action is not None
                else ""
            )
            solution_html = f"""
            <h2>✅ Reparatur durchgeführt</h2>
            <p>Es wurde ein fehlender Gegenverweis ergänzt.</p>
            {target_html}
            {line_html}
            """
        elif issue.repair_status == "SKIPPED":
            solution_html = """
            <h2>⚠ Keine Änderung erforderlich</h2>
            <p>Der vorgeschlagene Eintrag war bereits vorhanden.</p>
            <p>Die Daten waren bereits konsistent.</p>
            """
        elif issue.repair_status == "FAILED":
            solution_html = """
            <h2>❌ Reparatur fehlgeschlagen</h2>
            <p>Die Änderung konnte nicht durchgeführt werden.</p>
            <p>Bitte prüfen Sie die Daten manuell.</p>
            """
        elif repair_action is not None:
            target_html = resolved_record(
                "Zieldatensatz",
                repair_action.target_record,
            )
            solution_html = f"""
            <h2>Vorgeschlagene Lösung</h2>
            <p>Es wird ein fehlender Gegenverweis ergänzt.</p>
            {target_html}
            <p>Einzufügende Zeile:</p>
            <p><code>{escape(repair_action.new_line)}</code></p>
            """
        else:
            solution_html = """
            <h2>Lösung</h2>
            <p>Für diesen Fehler ist keine automatische Reparatur möglich.</p>
            <p>Bitte prüfen Sie die Quelldaten und die referenzierten
            Datensätze manuell.</p>
            """

        html = f"""
        <html>
        <body style="font-family:'Segoe UI';">
        <h2>Betroffene Datensätze</h2>
        {"".join(affected_records)}
        <hr>
        <h1>{escape(title)}<br>
        <small>({escape(issue.issue_type)})</small></h1>
        <h2>Fehlerbeschreibung</h2>
        {explanation_html}
        <hr>
        {solution_html}
        </body>
        </html>
        """

        self.detail_view.setHtml(html)

        self.issue_table.scrollToItem(
            item,
            QTableWidget.ScrollHint.PositionAtCenter
        )
    
    def on_table_sorted(
        self,
        logical_index,
        order
    ) -> None:

        QTimer.singleShot(
            0,
            self.scroll_current_row_into_view
        )
        
    def scroll_current_row_into_view(
        self
    ) -> None:

        row = self.issue_table.currentRow()

        if row < 0:
            return

        item = self.issue_table.item(
            row,
            0
        )

        if item is None:
            return

        self.issue_table.scrollToItem(
            item,
            QTableWidget.ScrollHint.PositionAtCenter
        )
        
    def restore_last_file(self) -> None:

        last_file = self.settings.value(
            "last_file",
            "",
            str
        )

        if not last_file:

            self.path_label.setText(
                str(Path.home())
            )

            return
        
        path = Path(last_file)

        if not path.exists():

            self.path_label.setText(
                str(path.parent)
            )

            return

        self.gedcom_file = str(path)

        self.filename_label.setText(
            path.name
        )

        self.path_label.setText(
            str(path.parent)
        )

        self.analyze_button.setEnabled(True)

        self.statusBar().showMessage(
            "Letzte Datei geladen - Bitte Analyse starten"
        )