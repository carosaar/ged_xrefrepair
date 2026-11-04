from dataclasses import dataclass


@dataclass(slots=True)
class Issue:
    issue_type: str
    description: str
    record_id: str
    auto_repair_possible: bool = False
