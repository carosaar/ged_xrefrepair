import pytest

from ged_xrefrepair.parser.gedcom_parser import GedcomParser


def test_load_raises_for_missing_file(tmp_path):
    missing_file = tmp_path / "missing.ged"

    with pytest.raises(FileNotFoundError):
        GedcomParser().load(str(missing_file))


def test_load_raises_for_invalid_utf8(tmp_path):
    gedcom_file = tmp_path / "invalid_encoding.ged"
    gedcom_file.write_bytes(b"0 HEAD\n\xff\n0 TRLR")

    with pytest.raises(UnicodeDecodeError):
        GedcomParser().load(str(gedcom_file))


def test_load_preserves_valid_utf8(tmp_path):
    gedcom_file = tmp_path / "valid.ged"
    gedcom_file.write_text(
        "0 @I1@ INDI\n1 NAME Jörg /Müller/\n0 TRLR",
        encoding="utf-8",
    )

    records = GedcomParser().load(str(gedcom_file))

    assert records[0].xref == "@I1@"
    assert records[0].lines[1] == "1 NAME Jörg /Müller/"
