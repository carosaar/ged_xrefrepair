from copy import deepcopy
from datetime import date
from pathlib import Path
import shutil

from ged_xrefrepair import __version__
from ged_xrefrepair.model.gedcom_record import GedcomRecord


class GedcomWriter:
    @staticmethod
    def _add_repair_history(
        records: list[GedcomRecord],
        repair_count: int,
        repair_date: date,
    ) -> list[GedcomRecord]:
        records_to_write = deepcopy(records)
        head = next(
            (record for record in records_to_write if record.tag == "HEAD"),
            None,
        )
        if head is None:
            return records_to_write

        text = (
            f"ged_XRefRepair {__version__}: am "
            f"{repair_date.strftime('%d.%m.%Y')} wurden "
            f"{repair_count} Zeigerreparaturen durchgeführt"
        )

        note_index = next(
            (
                index
                for index, line in enumerate(head.lines)
                if len(parts := line.split(maxsplit=2)) >= 2
                and parts[0] == "1"
                and parts[1] == "NOTE"
            ),
            None,
        )
        if note_index is None:
            head.lines.append(f"1 NOTE {text}")
            return records_to_write

        insert_index = note_index + 1
        while insert_index < len(head.lines):
            parts = head.lines[insert_index].split(maxsplit=2)
            if not parts or not parts[0].isdigit():
                break
            if int(parts[0]) <= 1:
                break
            insert_index += 1
        head.lines.insert(insert_index, f"2 CONT {text}")
        return records_to_write

    def create_backup(self, filename: str | Path) -> Path:
        source_path = Path(filename)
        if not source_path.is_file():
            raise FileNotFoundError(
                f"Die Originaldatei wurde nicht gefunden: {source_path}"
            )

        backup_path = Path(f"{source_path}.bak")
        shutil.copy2(source_path, backup_path)
        return backup_path

    def write(
        self,
        records: list[GedcomRecord],
        filename: str,
        repair_count: int = 0,
        repair_date: date | None = None,
    ) -> None:
        records_to_write = self._add_repair_history(
            records,
            repair_count,
            repair_date or date.today(),
        )
        content = "\n".join(
            line
            for record in records_to_write
            for line in record.lines
        )
        if content:
            content += "\n"

        Path(filename).write_text(content, encoding="utf-8")
        for original, saved in zip(records, records_to_write):
            if original.tag == "HEAD":
                original.lines[:] = saved.lines
                break
