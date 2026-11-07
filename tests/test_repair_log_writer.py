from datetime import datetime

from ged_xrefrepair.model.issue import Issue
from ged_xrefrepair.services.repair_log_writer import RepairLogWriter


def test_repair_log_is_created_with_repair_details_and_count(tmp_path):
    gedcom_path = tmp_path / "Familie.ged"
    repaired = Issue(
        "MISSING_CHIL",
        "Fehlender Kind-Verweis",
        "@F3@",
        "@I17@",
        True,
        "REPAIRED",
    )
    skipped = Issue(
        "MISSING_FAMC",
        "Fehlender Familien-Verweis",
        "@I18@",
        "@F3@",
        True,
        "SKIPPED",
    )

    log_path = RepairLogWriter().append_run(
        gedcom_path,
        [repaired, skipped],
        datetime(2026, 11, 7, 15, 20, 10),
    )

    assert log_path == tmp_path / "Familie.ged.repair.log"
    content = log_path.read_text(encoding="utf-8")
    assert "Version: 0.10.0" in content
    assert "Datum/Uhrzeit: 07.11.2026 15:20:10" in content
    assert "Dateiname: Familie.ged" in content
    assert "Anzahl Reparaturen: 1" in content
    assert "Problemtyp: MISSING_CHIL" in content
    assert "record_id: @F3@" in content
    assert "related_xref: @I17@" in content
    assert "action_type: ADD_CHIL" in content
    assert "Eingefügte Zeile: 1 CHIL @I17@" in content
    assert "SKIPPED" not in content


def test_repair_log_appends_each_repair_run(tmp_path):
    gedcom_path = tmp_path / "Familie.ged"
    writer = RepairLogWriter()
    first_repair = Issue(
        "MISSING_CHIL",
        "First",
        "@F1@",
        "@I1@",
        True,
        "REPAIRED",
    )
    second_repair = Issue(
        "MISSING_FAMC",
        "Second",
        "@I2@",
        "@F1@",
        True,
        "REPAIRED",
    )

    writer.append_run(
        gedcom_path,
        [first_repair],
        datetime(2026, 11, 7, 14, 0),
    )
    writer.append_run(
        gedcom_path,
        [second_repair],
        datetime(2026, 11, 7, 15, 0),
    )

    content = (tmp_path / "Familie.ged.repair.log").read_text(
        encoding="utf-8"
    )
    assert content.count("Reparaturprotokoll") == 2
    assert content.count("Anzahl Reparaturen: 1") == 2
    assert "Problemtyp: MISSING_CHIL" in content
    assert "Problemtyp: MISSING_FAMC" in content


def test_empty_repair_run_does_not_create_log_file(tmp_path):
    gedcom_path = tmp_path / "Familie.ged"
    skipped = Issue(
        "MISSING_CHIL",
        "Already present",
        "@F1@",
        "@I1@",
        True,
        "SKIPPED",
    )

    assert RepairLogWriter().append_run(gedcom_path, [skipped]) is None
    assert not (tmp_path / "Familie.ged.repair.log").exists()
