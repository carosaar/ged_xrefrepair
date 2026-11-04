from dataclasses import dataclass


@dataclass(slots=True)
class RepairAction:
    title: str
    record_id: str
    old_text: str
    new_text: str
    selected: bool = True
