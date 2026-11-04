# src/ged_xrefrepair/model/gedcom_record.py

from dataclasses import dataclass


@dataclass(slots=True)
class GedcomRecord:
    xref: str
    tag: str
    lines: list[str]