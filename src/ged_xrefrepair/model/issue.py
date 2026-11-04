from dataclasses import dataclass


@dataclass(slots=True)
class Issue:
    issue_type: str
    severity: str
    description: str
    auto_repair_possible: bool
