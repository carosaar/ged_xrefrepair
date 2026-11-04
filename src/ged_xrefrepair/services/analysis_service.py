# src/ged_xrefrepair/services/analysis_service.py

from ged_xrefrepair.parser.gedcom_parser import GedcomParser
from ged_xrefrepair.analyzer.validation_result import ValidationResult


class AnalysisService:

    def analyze(
        self,
        filename: str
    ) -> ValidationResult:

        parser = GedcomParser()

        records = parser.load(filename)

        individuals = 0
        families = 0

        for record in records:

            if record.tag == "INDI":
                individuals += 1

            elif record.tag == "FAM":
                families += 1

        return ValidationResult(
            individuals=individuals,
            families=families,
            records=len(records)
        )
