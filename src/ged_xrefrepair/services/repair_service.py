from copy import deepcopy
import logging

from ged_xrefrepair.model.gedcom_record import GedcomRecord
from ged_xrefrepair.model.issue import Issue, RepairStatus
from ged_xrefrepair.repair.repair_engine import RepairEngine
from ged_xrefrepair.services.repair_preview_service import (
    RepairPreviewService,
)

logger = logging.getLogger(__name__)


class RepairService:
    def __init__(
        self,
        preview_service: RepairPreviewService | None = None,
        repair_engine: RepairEngine | None = None,
    ) -> None:
        self.preview_service = preview_service or RepairPreviewService()
        self.repair_engine = repair_engine or RepairEngine()
        self._undo_stack: list[
            tuple[list[GedcomRecord], list[tuple[Issue, RepairStatus]]]
        ] = []
        self.last_changed_count = 0
        self.last_skipped_count = 0
        self.last_failed_count = 0

    @property
    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    def apply_selected(
        self,
        records: list[GedcomRecord],
        issues: list[Issue],
    ) -> list[GedcomRecord]:
        self.last_changed_count = 0
        self.last_skipped_count = 0
        self.last_failed_count = 0
        selected_issues = [
            issue for issue in issues if issue.auto_repair_possible
        ]
        if not selected_issues:
            return records

        snapshot = deepcopy(records)
        status_snapshot = [
            (issue, issue.repair_status)
            for issue in selected_issues
        ]
        self._undo_stack.append((snapshot, status_snapshot))

        for issue in selected_issues:
            try:
                action = self.preview_service.create_action(issue)
                if action is None:
                    raise ValueError(
                        "Für den als reparierbar markierten Problemtyp "
                        f"{issue.issue_type} gibt es keine Reparaturaktion"
                    )

                if self.repair_engine.apply(records, action):
                    issue.repair_status = "REPAIRED"
                    self.last_changed_count += 1
                else:
                    issue.repair_status = "SKIPPED"
                    self.last_skipped_count += 1
            except Exception:
                issue.repair_status = "FAILED"
                self.last_failed_count += 1
                logger.exception(
                    "Reparatur für %s (%s -> %s) fehlgeschlagen",
                    issue.issue_type,
                    issue.record_id,
                    issue.related_xref,
                )

        return records

    def undo(
        self,
        records: list[GedcomRecord],
    ) -> list[GedcomRecord]:
        if not self._undo_stack:
            raise ValueError("Es gibt keine Reparatur zum Rückgängigmachen")

        restored_records, issue_statuses = self._undo_stack.pop()
        records[:] = restored_records
        for issue, status in issue_statuses:
            issue.repair_status = status
        self.last_changed_count = 0
        self.last_skipped_count = 0
        self.last_failed_count = 0
        return records

    def clear_undo(self) -> None:
        self._undo_stack.clear()
        self.last_changed_count = 0
        self.last_skipped_count = 0
        self.last_failed_count = 0
