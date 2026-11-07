from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QWidget


class RepairLogWindow(QDialog):
    def __init__(
        self,
        parent: QWidget,
        log_content: str,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Reparaturprotokoll")
        self.resize(760, 520)

        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(log_content)
        layout.addWidget(self.text_edit)
