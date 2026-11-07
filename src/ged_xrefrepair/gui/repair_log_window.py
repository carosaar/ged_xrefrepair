from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QTextEdit,
    QWidget,
)


class RepairLogWindow(QDialog):
    def __init__(
        self,
        parent: QWidget,
        log_content: str,
        source_path: Path,
        can_save: bool = False,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("ged_XrefRepair - Reparaturprotokoll")
        self.resize(760, 520)
        self.source_path = source_path

        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(log_content)
        layout.addWidget(self.text_edit)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_button = QPushButton("💾 Protokoll speichern unter...")
        self.save_button.setEnabled(can_save)
        self.save_button.clicked.connect(self.save_log)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

    def save_log(self) -> None:
        default_path = Path(f"{self.source_path}.repair.log")
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Reparaturprotokoll speichern",
            str(default_path),
            "Protokolldateien (*.log);;Textdateien (*.txt);;Alle Dateien (*)",
        )
        if not filename:
            return

        try:
            Path(filename).write_text(
                self.text_edit.toPlainText(),
                encoding="utf-8",
            )
        except OSError as error:
            QMessageBox.critical(
                self,
                "Speichern fehlgeschlagen",
                f"Das Reparaturprotokoll konnte nicht gespeichert werden.\n\n"
                f"{error}",
            )
            return

        QMessageBox.information(
            self,
            "Protokoll gespeichert",
            f"Das Reparaturprotokoll wurde gespeichert:\n{filename}",
        )
