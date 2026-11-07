# src/ged_xrefrepair/services/repair_preview_service.py

from ged_xrefrepair.model.repair_action import (
    RepairAction
)


class RepairPreviewService:

    def create_action(
        self,
        issue
    ) -> RepairAction | None:
        if not issue.auto_repair_possible:
            return None

        action_data = {
            "MISSING_CHIL": (
                "ADD_CHIL",
                issue.related_xref,
                issue.record_id,
                "Kindreferenz ergänzen",
                f"1 CHIL {issue.related_xref}",
            ),
            "MISSING_FAMC": (
                "ADD_FAMC",
                issue.related_xref,
                issue.record_id,
                "Familienverweis ergänzen",
                f"1 FAMC {issue.related_xref}",
            ),
            "MISSING_HUSB": (
                "ADD_HUSB",
                issue.related_xref,
                issue.record_id,
                "Ehemann-Eintrag ergänzen",
                f"1 HUSB {issue.related_xref}",
            ),
            "MISSING_WIFE": (
                "ADD_WIFE",
                issue.related_xref,
                issue.record_id,
                "Ehefrau-Eintrag ergänzen",
                f"1 WIFE {issue.related_xref}",
            ),
            "MISSING_FAMS_HUSB": (
                "ADD_FAMS",
                issue.related_xref,
                issue.record_id,
                "Familienverweis beim Ehemann ergänzen",
                f"1 FAMS {issue.related_xref}",
            ),
            "MISSING_FAMS_WIFE": (
                "ADD_FAMS",
                issue.related_xref,
                issue.record_id,
                "Familienverweis bei der Ehefrau ergänzen",
                f"1 FAMS {issue.related_xref}",
            ),
        }
        action = action_data.get(issue.issue_type)
        if action is None:
            return None

        return RepairAction(
            action_type=action[0],
            source_record=action[1],
            target_record=action[2],
            description=action[3],
            new_line=action[4],
        )