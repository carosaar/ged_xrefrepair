from datetime import datetime
from pathlib import Path

from ged_xrefrepair import __version__
from ged_xrefrepair.model.issue import Issue
from ged_xrefrepair.services.repair_preview_service import (
    RepairPreviewService,
)


class RepairLogWriter:
    def __init__(
        self,
        preview_service: RepairPreviewService | None = None,
    ) -> None:
        self.preview_service = preview_service or RepairPreviewService()

    def append_run(
        self,
        gedcom_path: str | Path,
        issues: list[Issue],
        timestamp: datetime | None = None,
    ) -> Path | None:
        source_path = Path(gedcom_path)
        repaired_actions = [
            (issue, action)
            for issue in issues
            if issue.repair_status == "REPAIRED"
            if (action := self.preview_service.create_action(issue)) is not None
        ]
        if not repaired_actions:
            return None

        log_path = Path(f"{source_path}.repair.log")
        run_time = timestamp or datetime.now()
        lines = [
            "Reparaturprotokoll",
            f"Version: {__version__}",
            f"Datum/Uhrzeit: {run_time.strftime('%d.%m.%Y %H:%M:%S')}",
            f"Dateiname: {source_path.name}",
            f"Anzahl Reparaturen: {len(repaired_actions)}",
            "",
        ]

        for issue, action in repaired_actions:
            lines.extend(
                [
                    f"Problemtyp: {issue.issue_type}",
                    f"record_id: {issue.record_id}",
                    f"related_xref: {issue.related_xref}",
                    f"action_type: {action.action_type}",
                    f"Eingefügte Zeile: {action.new_line}",
                    "",
                ]
            )

        with log_path.open("a", encoding="utf-8", newline="\n") as log_file:
            log_file.write("\n".join(lines))
        return log_path
