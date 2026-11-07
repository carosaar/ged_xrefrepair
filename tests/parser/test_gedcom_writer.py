from datetime import date

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


def test_writer_adds_repair_history_note_when_head_has_no_note(tmp_path):
    output = tmp_path / "repaired.ged"
    records = [
        GedcomRecord("@HEAD@", "HEAD", ["0 HEAD", "1 SOUR Ahnenblatt"]),
        GedcomRecord("@I1@", "INDI", ["0 @I1@ INDI", "1 NAME Max"]),
    ]

    GedcomWriter().write(
        records,
        str(output),
        repair_count=17,
        repair_date=date(2026, 11, 4),
    )

    lines = output.read_text(encoding="utf-8").splitlines()
    assert lines[:3] == [
        "0 HEAD",
        "1 SOUR Ahnenblatt",
        "1 NOTE ged_XRefRepair 0.10.0: am 04.11.2026 wurden "
        "17 Zeigerreparaturen durchgeführt",
    ]
    assert records[0].lines == [
        "0 HEAD",
        "1 SOUR Ahnenblatt",
        "1 NOTE ged_XRefRepair 0.10.0: am 04.11.2026 wurden "
        "17 Zeigerreparaturen durchgeführt",
    ]
    assert records[1].lines == ["0 @I1@ INDI", "1 NAME Max"]


def test_writer_appends_cont_to_existing_note_block(tmp_path):
    output = tmp_path / "repaired.ged"
    records = [
        GedcomRecord(
            "@HEAD@",
            "HEAD",
            [
                "0 HEAD",
                "1 NOTE Datei aus Altbestand",
                "2 CONT Bearbeitet 2020",
                "1 SOUR Ahnenblatt",
            ],
        ),
    ]

    GedcomWriter().write(
        records,
        str(output),
        repair_count=3,
        repair_date=date(2026, 11, 5),
    )

    assert output.read_text(encoding="utf-8").splitlines() == [
        "0 HEAD",
        "1 NOTE Datei aus Altbestand",
        "2 CONT Bearbeitet 2020",
        "2 CONT ged_XRefRepair 0.10.0: am 05.11.2026 wurden "
        "3 Zeigerreparaturen durchgeführt",
        "1 SOUR Ahnenblatt",
    ]


def test_writer_keeps_multiple_cont_lines_and_appends_new_history_entry(
    tmp_path,
):
    output = tmp_path / "repaired.ged"
    records = [
        GedcomRecord(
            "@HEAD@",
            "HEAD",
            [
                "0 HEAD",
                "1 NOTE Datei aus Altbestand",
                "2 CONT Bearbeitet 2020",
                "2 CONT Ergänzung",
            ],
        ),
    ]

    GedcomWriter().write(
        records,
        str(output),
        repair_count=12,
        repair_date=date(2026, 11, 4),
    )

    assert output.read_text(encoding="utf-8").splitlines() == [
        "0 HEAD",
        "1 NOTE Datei aus Altbestand",
        "2 CONT Bearbeitet 2020",
        "2 CONT Ergänzung",
        "2 CONT ged_XRefRepair 0.10.0: am 04.11.2026 wurden "
        "12 Zeigerreparaturen durchgeführt",
    ]


def test_writer_appends_a_new_note_for_each_save(tmp_path):
    output = tmp_path / "repaired.ged"
    records = [GedcomRecord("@HEAD@", "HEAD", ["0 HEAD"])]
    writer = GedcomWriter()

    writer.write(
        records,
        str(output),
        repair_count=12,
        repair_date=date(2026, 11, 4),
    )
    writer.write(
        records,
        str(output),
        repair_count=3,
        repair_date=date(2026, 11, 5),
    )

    assert output.read_text(encoding="utf-8").splitlines() == [
        "0 HEAD",
        "1 NOTE ged_XRefRepair 0.10.0: am 04.11.2026 wurden "
        "12 Zeigerreparaturen durchgeführt",
        "2 CONT ged_XRefRepair 0.10.0: am 05.11.2026 wurden "
        "3 Zeigerreparaturen durchgeführt",
    ]


def test_writer_saves_without_history_when_head_is_missing(tmp_path):
    output = tmp_path / "no_head.ged"
    records = [
        GedcomRecord("@I1@", "INDI", ["0 @I1@ INDI", "1 NAME Max"]),
    ]

    GedcomWriter().write(
        records,
        str(output),
        repair_count=1,
        repair_date=date(2026, 11, 4),
    )

    assert output.read_text(encoding="utf-8") == (
        "0 @I1@ INDI\n1 NAME Max\n"
    )
    assert records[0].lines == ["0 @I1@ INDI", "1 NAME Max"]
