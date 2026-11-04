# src/ged_xrefrepair/analyzer/validation_result.py

from dataclasses import dataclass


@dataclass(slots=True)
class ValidationResult:
    individuals: int
    families: int
    records: int