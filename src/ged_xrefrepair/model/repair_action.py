# src/ged_xrefrepair/model/repair_action.py
from dataclasses import dataclass


@dataclass(slots=True)
class RepairAction:

    action_type: str

    target_record: str

    description: str

    new_line: str