# tests/test_repair_preview.py

from ged_xrefrepair.model.issue import Issue
from ged_xrefrepair.services.repair_preview_service import (
    RepairPreviewService
)


def test_missing_chil_preview():

    issue = Issue(
        issue_type="MISSING_CHIL",
        record_id="@F1@",
        related_xref="@I1@",
        description="Test",
        auto_repair_possible=True,
    )

    action = (
        RepairPreviewService()
        .create_action(issue)
    )

    assert action is not None

    assert action.action_type == "ADD_CHIL"

    assert action.target_record == "@F1@"

    assert action.source_record == "@I1@"

    assert action.new_line == "1 CHIL @I1@"