from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

from ged_xrefrepair import __version__
from ged_xrefrepair.model.issue import Issue
from ged_xrefrepair.services.repair_preview_service import (
    RepairPreviewService,
)


class RepairLogWriter:
    TITLE = "ged_XrefRepair - Reparaturprotokoll"

    @dataclass(frozen=True)
    class Run:
        timestamp: datetime
        issues: tuple[Issue, ...]

    def __init__(
        self,
        preview_service: RepairPreviewService | None = None,
    ) -> None:
        self.preview_service = preview_service or RepairPreviewService()

    def render(
        self,
        gedcom_path: str | Path,
        runs: list[Run],
    ) -> str:
        source_path = Path(gedcom_path)
        rendered_runs: list[str] = []
        for run in runs:
            repaired_actions = [
                (issue, action)
                for issue in run.issues
                if issue.repair_status == "REPAIRED"
                if (
                    action := self.preview_service.create_action(issue)
                ) is not None
            ]
            if not repaired_actions:
                continue

            lines = [
                self.TITLE,
                f"Version: {__version__}",
                f"Datum/Uhrzeit: "
                f"{run.timestamp.strftime('%d.%m.%Y %H:%M:%S')}",
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
            rendered_runs.append("\n".join(lines))

        return "\n".join(rendered_runs)

    def write(
        self,
        gedcom_path: str | Path,
        runs: list[Run],
    ) -> Path | None:
        content = self.render(gedcom_path, runs)
        if not content:
            return None

        log_path = Path(f"{gedcom_path}.repair.log")
        log_path.write_text(content, encoding="utf-8", newline="\n")
        return log_path
