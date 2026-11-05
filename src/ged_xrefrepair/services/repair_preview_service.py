# src/ged_xrefrepair/services/repair_preview_service.py

from ged_xrefrepair.model.repair_action import (
    RepairAction
)


class RepairPreviewService:

    def create_action(
        self,
        issue
    ) -> RepairAction | None:

        if issue.issue_type == "MISSING_CHIL":

            return RepairAction(
                action_type="ADD_CHIL",
                target_record=issue.record_id,
                description=(
                    "Kindreferenz ergänzen"
                ),
                new_line=(
                    f"1 CHIL "
                    f"{issue.related_xref}"
                ),
            )

        return None