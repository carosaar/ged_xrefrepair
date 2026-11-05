# src/ged_xrefrepair/services/analysis_service.py

from ged_xrefrepair.parser.gedcom_parser import GedcomParser
from ged_xrefrepair.analyzer.reference_analyzer import ReferenceAnalyzer
from ged_xrefrepair.analyzer.analysis_result import AnalysisResult


class AnalysisService:

    def analyze(
        self,
        filename: str
    ) -> AnalysisResult:

        parser = GedcomParser()

        records = parser.load(filename)

        individuals = 0
        families = 0

        for record in records:

            if record.tag == "INDI":
                individuals += 1

            elif record.tag == "FAM":
                families += 1

        analyzer = ReferenceAnalyzer()

        issues = analyzer.analyze(records)

#       Zeige das Ergebnis der Analyse
#       for issue in issues:
#           print(issue)

        return AnalysisResult(
            individuals=individuals,
            families=families,
            records=len(records),
            issues_count=len(issues),
            issues=issues,
            record_list=records
        )