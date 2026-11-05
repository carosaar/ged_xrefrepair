# src/ged_xrefrepair/analyzer/analysis_result.py

from dataclasses import dataclass
from ged_xrefrepair.model.issue import Issue
from ged_xrefrepair.model.gedcom_record import GedcomRecord

@dataclass(slots=True)
class AnalysisResult:
    individuals: int
    families: int
    records: int
    issues_count: int

    issues: list[Issue]

    record_list: list[GedcomRecord]
    