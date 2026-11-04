# src/ged_xrefrepair/analyzer/analysis_result.py

from dataclasses import dataclass
from ged_xrefrepair.model.issue import Issue

@dataclass(slots=True)
class AnalysisResult:
    individuals: int
    families: int
    records: int
    issues_count: int
    issues: list[Issue]