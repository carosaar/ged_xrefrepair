from ged_xrefrepair.model.gedcom_record import GedcomRecord
from ged_xrefrepair.parser.gedcom_writer import GedcomWriter


def test_writer_serializes_changed_records_in_order(tmp_path):
    output = tmp_path / "repaired.ged"
    records = [
        GedcomRecord(
            "@I1@",
            "INDI",
            ["0 @I1@ INDI", "1 NAME Max", "1 FAMC @F1@"],
        ),
        GedcomRecord(
            "@F1@",
            "FAM",
            ["0 @F1@ FAM", "1 CHIL @I1@"],
        ),
    ]

    GedcomWriter().write(records, str(output))

    assert output.read_text(encoding="utf-8") == (
        "0 @I1@ INDI\n"
        "1 NAME Max\n"
        "1 FAMC @F1@\n"
        "0 @F1@ FAM\n"
        "1 CHIL @I1@\n"
    )


def test_writer_creates_backup_and_overwrites_previous_backup(tmp_path):
    source = tmp_path / "source.ged"
    backup = tmp_path / "source.ged.bak"
    source.write_text("original", encoding="utf-8")
    backup.write_text("old backup", encoding="utf-8")

    backup_path = GedcomWriter().create_backup(source)

    assert backup_path == backup
    assert backup.read_text(encoding="utf-8") == "original"

    source.write_text("updated original", encoding="utf-8")
    GedcomWriter().create_backup(source)

    assert backup.read_text(encoding="utf-8") == "updated original"


def test_writer_reports_missing_backup_source(tmp_path):
    missing_source = tmp_path / "missing.ged"

    try:
        GedcomWriter().create_backup(missing_source)
    except FileNotFoundError as error:
        assert str(missing_source) in str(error)
    else:
        raise AssertionError("Expected FileNotFoundError")
