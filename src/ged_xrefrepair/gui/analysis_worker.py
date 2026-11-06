import logging

from PySide6.QtCore import QObject, Signal, Slot

from ged_xrefrepair.services.analysis_service import AnalysisService


logger = logging.getLogger(__name__)


class AnalysisWorker(QObject):
    result_ready = Signal(object)
    failed = Signal(object)
    finished = Signal()

    def __init__(self, filename: str) -> None:
        super().__init__()
        self.filename = filename

    @Slot()
    def run(self) -> None:
        try:
            result = AnalysisService().analyze(self.filename)
        except Exception as error:
            logger.exception(
                "Analysis failed for %s",
                self.filename,
            )
            self.failed.emit(error)
        else:
            self.result_ready.emit(result)
        finally:
            self.finished.emit()
