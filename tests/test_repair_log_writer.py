from datetime import datetime

from ged_xrefrepair import __version__
from ged_xrefrepair.model.issue import Issue
from ged_xrefrepair.services.repair_log_writer import RepairLogWriter


def test_repair_log_is_written_with_repair_details_and_count(tmp_path):
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

    run = RepairLogWriter.Run(
        datetime(2026, 11, 7, 15, 20, 10),
        (repaired, skipped),
    )
    log_path = RepairLogWriter().write(gedcom_path, [run])

    assert log_path == tmp_path / "Familie.ged.repair.log"
    content = log_path.read_text(encoding="utf-8")
    assert f"Version: {__version__}" in content
    assert "Datum/Uhrzeit: 07.11.2026 15:20:10" in content
    assert "Dateiname: Familie.ged" in content
    assert "Anzahl Reparaturen: 1" in content
    assert "Problemtyp: MISSING_CHIL" in content
    assert "record_id: @F3@" in content
    assert "related_xref: @I17@" in content
    assert "action_type: ADD_CHIL" in content
    assert "Eingefügte Zeile: 1 CHIL @I17@" in content
    assert "SKIPPED" not in content


def test_repair_log_is_rebuilt_from_all_repair_runs(tmp_path):
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

    runs = [
        RepairLogWriter.Run(
            datetime(2026, 11, 7, 14, 0),
            (first_repair,),
        ),
        RepairLogWriter.Run(
            datetime(2026, 11, 7, 15, 0),
            (second_repair,),
        ),
    ]
    log_path = writer.write(gedcom_path, runs)
    assert log_path is not None

    content = log_path.read_text(encoding="utf-8")
    assert content.count("ged_XrefRepair - Reparaturprotokoll") == 2
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

    run = RepairLogWriter.Run(datetime.now(), (skipped,))
    assert RepairLogWriter().write(gedcom_path, [run]) is None
    assert not (tmp_path / "Familie.ged.repair.log").exists()


def test_writing_protocol_overwrites_old_content_with_fresh_report(tmp_path):
    gedcom_path = tmp_path / "Familie.ged"
    log_path = tmp_path / "Familie.ged.repair.log"
    log_path.write_text(
        "alte Daten\n",
        encoding="utf-8",
    )
    issue = Issue(
        "MISSING_CHIL",
        "New repair",
        "@F1@",
        "@I1@",
        True,
        "REPAIRED",
    )

    run = RepairLogWriter.Run(
        datetime(2026, 11, 7, 16, 0),
        (issue,),
    )
    RepairLogWriter().write(
        gedcom_path,
        [run],
    )

    content = log_path.read_text(encoding="utf-8")
    assert content.count("ged_XrefRepair - Reparaturprotokoll") == 1
    assert "alte Daten" not in content
    assert "Anzahl Reparaturen: 1" in content
    assert "Datum/Uhrzeit: 07.11.2026 16:00:00" in content
