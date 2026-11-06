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

                source_record=
                    issue.related_xref,

                target_record=
                    issue.record_id,

                description=
                    "Kindreferenz ergänzen",

                new_line=
                    f"1 CHIL {issue.related_xref}",
            )

        return None