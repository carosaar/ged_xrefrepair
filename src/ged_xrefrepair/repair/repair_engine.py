from ged_xrefrepair.model.gedcom_record import GedcomRecord
from ged_xrefrepair.model.repair_action import RepairAction


class RepairEngine:
    ACTIONS = {
        "ADD_CHIL": ("FAM", "CHIL"),
        "ADD_FAMC": ("INDI", "FAMC"),
        "ADD_HUSB": ("FAM", "HUSB"),
        "ADD_WIFE": ("FAM", "WIFE"),
        "ADD_FAMS": ("INDI", "FAMS"),
    }

    def apply(
        self,
        records: list[GedcomRecord],
        action: RepairAction,
    ) -> bool:
        action_definition = self.ACTIONS.get(action.action_type)
        if action_definition is None:
            raise ValueError(
                f"Nicht unterstützte Reparaturaktion: {action.action_type}"
            )

        expected_tag, reference_tag = action_definition
        expected_line = f"1 {reference_tag} {action.source_record}"
        if action.new_line != expected_line:
            raise ValueError(
                f"Ungültige Zeile für Reparaturaktion {action.action_type}"
            )

        matching_records = [
            record
            for record in records
            if record.xref == action.target_record
        ]
        if not matching_records:
            raise ValueError(
                f"Zieldatensatz {action.target_record} wurde nicht gefunden"
            )
        if len(matching_records) > 1:
            raise ValueError(
                f"Zieldatensatz {action.target_record} ist nicht eindeutig"
            )

        target = matching_records[0]
        if target.tag != expected_tag:
            raise ValueError(
                f"Reparaturaktion {action.action_type} erwartet einen "
                f"{expected_tag}-Datensatz, gefunden wurde {target.tag}"
            )

        if action.new_line in target.lines:
            return False

        target.lines.append(action.new_line)
        return True
