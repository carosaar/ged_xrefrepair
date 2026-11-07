from pathlib import Path
import shutil

from ged_xrefrepair.model.gedcom_record import GedcomRecord


class GedcomWriter:
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
    ) -> None:
        content = "\n".join(
            line
            for record in records
            for line in record.lines
        )
        if content:
            content += "\n"

        Path(filename).write_text(content, encoding="utf-8")
