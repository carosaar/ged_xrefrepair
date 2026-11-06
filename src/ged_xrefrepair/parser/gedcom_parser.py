# src/ged_xrefrepair/parser/gedcom_parser.py

from pathlib import Path

from ged_xrefrepair.model.gedcom_record import GedcomRecord


class GedcomParser:

    def load(self, filename: str) -> list[GedcomRecord]:

        path = Path(filename)

        lines = path.read_text(
            encoding="utf-8"
        ).splitlines()

        records = []

        current = []

        for line in lines:

            if line.startswith("0 ") and current:
                records.append(
                    self._create_record(current)
                )
                current = []

            current.append(line)

        if current:
            records.append(
                self._create_record(current)
            )

        return records

    def _create_record(
        self,
        lines: list[str]
    ) -> GedcomRecord:

        first = lines[0]

        parts = first.split()

        xref = ""

        tag = ""

        if len(parts) >= 3 and parts[1].startswith("@"):
            xref = parts[1]
            tag = parts[2]

        elif len(parts) >= 2:
            tag = parts[1]

        return GedcomRecord(
            xref=xref,
            tag=tag,
            lines=lines
        )