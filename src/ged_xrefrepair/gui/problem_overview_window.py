from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class ProblemOverviewWindow(QDialog):
    HEADERS = (
        "Problemtyp",
        "Bedeutung",
        "Automatisch lösbar?",
        "Bedingung / Hinweis",
    )

    PROBLEMS = (
        (
            "MISSING_CHIL",
            "FAMC verweist auf Familie ohne passenden CHIL.",
            "Ja.",
            "Person und Familie vorhanden. Andere CHIL-Zuordnungen und PEDI "
            "sind unerheblich. Fehlt die Familie: MISSING_FAMILY.",
        ),
        (
            "MISSING_FAMC",
            "CHIL verweist auf Person ohne passenden FAMC.",
            "Ja.",
            "Person und Familie vorhanden. Andere FAMC-Zuordnungen und PEDI "
            "sind unerheblich. Fehlt die Person: MISSING_PERSON.",
        ),
        (
            "MISSING_HUSB",
            "FAMS verweist auf Familie ohne passenden HUSB.",
            "Ja, wenn eindeutig.",
            "SEX M und einziger passender Kandidat; sonst keine automatische "
            "Zuordnung.",
        ),
        (
            "MISSING_WIFE",
            "FAMS verweist auf Familie ohne passenden WIFE.",
            "Ja, wenn eindeutig.",
            "SEX F und einziger passender Kandidat; sonst keine automatische "
            "Zuordnung.",
        ),
        (
            "MISSING_FAMS_HUSB",
            "HUSB ohne passenden FAMS-Rückverweis.",
            "Ja, wenn eindeutig.",
            "Person vorhanden, SEX M.",
        ),
        (
            "MISSING_FAMS_WIFE",
            "WIFE ohne passenden FAMS-Rückverweis.",
            "Ja, wenn eindeutig.",
            "Person vorhanden, SEX F.",
        ),
        (
            "MISSING_PERSON",
            "HUSB-, WIFE- oder CHIL-Verweis auf fehlende Person.",
            "Nein.",
            "Personendatensatz oder richtige XRef manuell klären.",
        ),
        (
            "MISSING_FAMILY",
            "FAMC- oder FAMS-Verweis auf fehlende Familie.",
            "Nein.",
            "Familiendatensatz oder richtige XRef manuell klären.",
        ),
    )

    def __init__(self, parent=None) -> None:
        super().__init__(parent, Qt.WindowType.Window)
        self.setWindowTitle("Hilfe - Problemübersicht")
        self.setMinimumSize(1000, 480)

        layout = QVBoxLayout(self)
        explanation = QLabel(
            "Die Übersicht beschreibt die vom Analyzer erkannten "
            "Referenzprobleme und wann eine Zuordnung eindeutig ist. "
            "Mehrere FAMC-Verweise werden nicht als eigener Problemfall "
            "bewertet. PEDI-Untertags beeinflussen den Abgleich von FAMC "
            "und CHIL nicht. "
            "„Automatisch lösbar“ bezeichnet die fachliche Eindeutigkeit "
            "des Befunds; die Anwendung ändert die GEDCOM-Datei dadurch "
            "nicht automatisch. Prüfen Sie Vorschläge vor jeder Änderung "
            "anhand Ihrer Quelldaten."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        self.problem_table = QTableWidget(
            len(self.PROBLEMS),
            len(self.HEADERS),
            self,
        )
        self.problem_table.setObjectName("problemOverviewTable")
        self.problem_table.setHorizontalHeaderLabels(self.HEADERS)
        self.problem_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.problem_table.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )
        self.problem_table.setWordWrap(True)
        self.problem_table.verticalHeader().hide()

        for row, problem in enumerate(self.PROBLEMS):
            for column, text in enumerate(problem):
                item = QTableWidgetItem(text)
                item.setFlags(
                    item.flags()
                    & ~Qt.ItemFlag.ItemIsEditable
                )
                self.problem_table.setItem(row, column, item)

        header = self.problem_table.horizontalHeader()
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Fixed,
        )
        self.problem_table.setColumnWidth(0, 150)
        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Fixed,
        )
        self.problem_table.setColumnWidth(2, 155)
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )
        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.Stretch,
        )
        layout.addWidget(self.problem_table)
        QTimer.singleShot(0, self.problem_table.resizeRowsToContents)
