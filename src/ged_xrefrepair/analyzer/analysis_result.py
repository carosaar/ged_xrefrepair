# src/ged_xrefrepair/analyzer/analysis_result.py

from dataclasses import dataclass


@dataclass(slots=True)
class AnalysisResult:
    individuals: int
    families: int
    records: int
    issues: int