import pytest

from ged_xrefrepair.model.gedcom_record import GedcomRecord
from ged_xrefrepair.model.issue import Issue
from ged_xrefrepair.repair.repair_engine import RepairEngine
from ged_xrefrepair.services.repair_preview_service import (
    RepairPreviewService,
)
from ged_xrefrepair.services.repair_service import RepairService


@pytest.mark.parametrize(
    (
        "issue_type",
        "record_xref",
        "record_tag",
        "related_xref",
        "related_tag",
        "expected_action_type",
        "expected_target",
        "expected_line",
    ),
    [
        (
            "MISSING_CHIL",
            "@F1@",
            "FAM",
            "@I1@",
            "INDI",
            "ADD_CHIL",
            "@F1@",
            "1 CHIL @I1@",
        ),
        (
            "MISSING_FAMC",
            "@I1@",
            "INDI",
            "@F1@",
            "FAM",
            "ADD_FAMC",
            "@I1@",
            "1 FAMC @F1@",
        ),
        (
            "MISSING_HUSB",
            "@F1@",
            "FAM",
            "@I1@",
            "INDI",
            "ADD_HUSB",
            "@F1@",
            "1 HUSB @I1@",
        ),
        (
            "MISSING_WIFE",
            "@F1@",
            "FAM",
            "@I2@",
            "INDI",
            "ADD_WIFE",
            "@F1@",
            "1 WIFE @I2@",
        ),
        (
            "MISSING_FAMS_HUSB",
            "@I1@",
            "INDI",
            "@F1@",
            "FAM",
            "ADD_FAMS",
            "@I1@",
            "1 FAMS @F1@",
        ),
        (
            "MISSING_FAMS_WIFE",
            "@I2@",
            "INDI",
            "@F1@",
            "FAM",
            "ADD_FAMS",
            "@I2@",
            "1 FAMS @F1@",
        ),
    ],
)
def test_selected_repairable_issues_are_applied(
    issue_type,
    record_xref,
    record_tag,
    related_xref,
    related_tag,
    expected_action_type,
    expected_target,
    expected_line,
):
    records = [
        GedcomRecord(
            xref=record_xref,
            tag=record_tag,
            lines=[f"0 {record_xref} {record_tag}"],
        ),
        GedcomRecord(
            xref=related_xref,
            tag=related_tag,
            lines=[f"0 {related_xref} {related_tag}"],
        ),
    ]
    issue = Issue(
        issue_type=issue_type,
        record_id=record_xref,
        related_xref=related_xref,
        description="Test",
        auto_repair_possible=True,
    )

    action = RepairPreviewService().create_action(issue)
    assert action is not None
    assert action.action_type == expected_action_type
    assert action.source_record == related_xref
    assert action.target_record == expected_target
    assert action.new_line == expected_line

    service = RepairService()
    updated_records = service.apply_selected(records, [issue])

    assert updated_records is records
    assert service.last_changed_count == 1
    target = next(
        record
        for record in records
        if record.xref == expected_target
    )
    assert target.lines[-1] == expected_line


@pytest.mark.parametrize(
    ("issue_type", "record_id", "related_xref"),
    [
        ("MISSING_PERSON", "@F1@", "@I404@"),
        ("MISSING_FAMILY", "@I1@", "@F404@"),
        ("MISSING_HUSB", "@F1@", "@I404@"),
    ],
)
def test_nonrepairable_issues_are_ignored(
    issue_type,
    record_id,
    related_xref,
):
    records = [
        GedcomRecord("@I1@", "INDI", ["0 @I1@ INDI"]),
        GedcomRecord("@F1@", "FAM", ["0 @F1@ FAM"]),
    ]
    original_lines = [record.lines.copy() for record in records]
    issue = Issue(
        issue_type=issue_type,
        record_id=record_id,
        related_xref=related_xref,
        description="Not repairable",
        auto_repair_possible=False,
    )

    service = RepairService()
    assert service.apply_selected(records, [issue]) is records
    assert service.last_changed_count == 0
    assert [record.lines for record in records] == original_lines


def test_preview_does_not_offer_action_for_nonrepairable_issue():
    issue = Issue(
        "MISSING_HUSB",
        "Ambiguous candidate",
        "@F1@",
        "@I1@",
        False,
    )

    assert RepairPreviewService().create_action(issue) is None


def test_engine_does_not_add_duplicate_line_and_is_idempotent():
    target = GedcomRecord(
        "@F1@",
        "FAM",
        ["0 @F1@ FAM", "1 CHIL @I1@"],
    )
    source = GedcomRecord("@I1@", "INDI", ["0 @I1@ INDI"])
    action = RepairPreviewService().create_action(
        Issue(
            "MISSING_CHIL",
            "Test",
            "@F1@",
            "@I1@",
            True,
        )
    )
    assert action is not None

    engine = RepairEngine()

    assert engine.apply([target, source], action) is False
    assert engine.apply([target, source], action) is False
    assert target.lines.count("1 CHIL @I1@") == 1


def test_engine_adds_line_to_target_without_modifying_other_records():
    target = GedcomRecord("@F1@", "FAM", ["0 @F1@ FAM", "1 NOTE keep"])
    action = RepairPreviewService().create_action(
        Issue("MISSING_CHIL", "Test", "@F1@", "@I1@", True)
    )
    assert action is not None

    assert RepairEngine().apply([target], action) is True
    assert target.lines == [
        "0 @F1@ FAM",
        "1 NOTE keep",
        "1 CHIL @I1@",
    ]


def test_repair_service_is_idempotent_for_repeated_issue():
    records = [
        GedcomRecord("@F1@", "FAM", ["0 @F1@ FAM"]),
        GedcomRecord("@I1@", "INDI", ["0 @I1@ INDI"]),
    ]
    issue = Issue(
        "MISSING_CHIL",
        "Test",
        "@F1@",
        "@I1@",
        True,
    )
    service = RepairService()

    assert service.apply_selected(records, [issue]) is records
    assert service.last_changed_count == 1
    assert service.apply_selected(records, [issue]) is records
    assert service.last_changed_count == 0
    assert records[0].lines.count("1 CHIL @I1@") == 1


def test_engine_rejects_missing_or_wrong_type_target():
    action = RepairPreviewService().create_action(
        Issue(
            "MISSING_CHIL",
            "Test",
            "@F1@",
            "@I1@",
            True,
        )
    )
    assert action is not None

    with pytest.raises(ValueError, match="wurde nicht gefunden"):
        RepairEngine().apply(
            [GedcomRecord("@I1@", "INDI", ["0 @I1@ INDI"])],
            action,
        )

    with pytest.raises(ValueError, match="erwartet einen FAM-Datensatz"):
        RepairEngine().apply(
            [
                GedcomRecord("@F1@", "INDI", ["0 @F1@ INDI"]),
                GedcomRecord("@I1@", "INDI", ["0 @I1@ INDI"]),
            ],
            action,
        )


def test_repair_service_supports_multiple_full_undo_snapshots():
    records = [
        GedcomRecord(
            "@I1@",
            "INDI",
            ["0 @I1@ INDI", "1 NAME Original"],
        ),
        GedcomRecord("@F1@", "FAM", ["0 @F1@ FAM"]),
    ]
    service = RepairService()
    original_lines = [record.lines.copy() for record in records]

    first_issue = Issue(
        "MISSING_CHIL",
        "First round",
        "@F1@",
        "@I1@",
        True,
    )
    service.apply_selected(records, [first_issue])
    assert records[1].lines[-1] == "1 CHIL @I1@"
    assert service.can_undo

    records[0].lines.append("1 NOTE external mutation")
    second_issue = Issue(
        "MISSING_FAMC",
        "Second round",
        "@I1@",
        "@F1@",
        True,
    )
    service.apply_selected(records, [second_issue])
    assert records[0].lines[-1] == "1 FAMC @F1@"

    service.undo(records)
    assert records[0].lines == [
        "0 @I1@ INDI",
        "1 NAME Original",
        "1 NOTE external mutation",
    ]
    assert records[1].lines == ["0 @F1@ FAM", "1 CHIL @I1@"]
    assert service.can_undo

    service.undo(records)
    assert [record.lines for record in records] == original_lines
    assert not service.can_undo

    with pytest.raises(ValueError, match="keine Reparatur"):
        service.undo(records)


def test_failed_repair_is_reported_without_aborting_other_repairs():
    records = [
        GedcomRecord("@F1@", "FAM", ["0 @F1@ FAM"]),
        GedcomRecord("@I1@", "INDI", ["0 @I1@ INDI"]),
    ]
    original = [record.lines.copy() for record in records]
    service = RepairService()
    issues = [
        Issue("MISSING_CHIL", "Valid", "@F1@", "@I1@", True),
        Issue("MISSING_CHIL", "Invalid target", "@F404@", "@I1@", True),
    ]

    service.apply_selected(records, issues)

    assert records[1].lines == ["0 @I1@ INDI"]
    assert records[0].lines == original[0] + ["1 CHIL @I1@"]
    assert issues[0].repair_status == "REPAIRED"
    assert issues[1].repair_status == "FAILED"
    assert service.last_changed_count == 1
    assert service.last_failed_count == 1
    assert service.can_undo

    service.undo(records)
    assert [record.lines for record in records] == original
    assert issues[0].repair_status == "NOT_PROCESSED"
    assert issues[1].repair_status == "NOT_PROCESSED"


def test_duplicate_repair_is_skipped_and_undo_restores_status():
    records = [
        GedcomRecord(
            "@F1@",
            "FAM",
            ["0 @F1@ FAM", "1 CHIL @I1@"],
        ),
        GedcomRecord("@I1@", "INDI", ["0 @I1@ INDI"]),
    ]
    issue = Issue("MISSING_CHIL", "Test", "@F1@", "@I1@", True)
    service = RepairService()

    service.apply_selected(records, [issue])

    assert issue.repair_status == "SKIPPED"
    assert service.last_skipped_count == 1
    assert service.last_changed_count == 0
    service.undo(records)
    assert issue.repair_status == "NOT_PROCESSED"
