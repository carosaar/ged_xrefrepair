# src/ged_xrefrepair/model/issue.py
from dataclasses import dataclass
from typing import Literal


RepairStatus = Literal[
    "NOT_PROCESSED",
    "REPAIRED",
    "SKIPPED",
    "FAILED",
]


@dataclass(slots=True)
class Issue:
    issue_type: str
    description: str
    
    # Datensatz mit dem Fehler
    record_id: str
    
    # Verweis auf den Datensatz, auf den der fehlerhafte Datensatz verweist
    related_xref: str
    
    # Gibt an, ob der Fehler automatisch behoben werden kann
    auto_repair_possible: bool = False

    repair_status: RepairStatus = "NOT_PROCESSED"
