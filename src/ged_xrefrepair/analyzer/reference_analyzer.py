import re

from ged_xrefrepair.analyzer.rules.missing_family import (
    MissingFamilyRule
)

from ged_xrefrepair.analyzer.rules.missing_chil import (
    MissingChilRule
)

from ged_xrefrepair.model.issue import Issue
from ged_xrefrepair.model.gedcom_record import GedcomRecord


class ReferenceAnalyzer:

    famc_pattern = re.compile(
        r"1 FAMC (@[^@]+@)"
    )

    chil_pattern = re.compile(
        r"1 CHIL (@[^@]+@)"
    )

    def analyze(
        self,
        records: list[GedcomRecord]
    ) -> list[Issue]:

        issues = []
        
        missing_family_rule = MissingFamilyRule()

        missing_chil_rule = MissingChilRule()

        families = {}

        child_families = {}

        #
        # Familienindex aufbauen
        #

        for record in records:

            if record.tag != "FAM":
                continue

            children = set()

            for line in record.lines:

                match = self.chil_pattern.match(
                    line
                )

                if match:

                    child_xref = match.group(1)

                    children.add(
                        child_xref
                    )

                    child_families.setdefault(
                        child_xref,
                        set()
                    ).add(
                        record.xref
                    )

            families[record.xref] = children

        #
        # Personen prüfen
        #

        for record in records:

            if record.tag != "INDI":
                continue

            for line in record.lines:

                match = self.famc_pattern.match(
                    line
                )

                if not match:
                    continue

                family_xref = match.group(1)

                #
                # Referenzierte Familie fehlt
                #

                issues.extend(
                    missing_family_rule.analyze(
                        record,
                        family_xref,
                        families,
                    )
                )

                if family_xref not in families:
                    continue

                #
                # CHIL-Eintrag fehlt
                #

                issues.extend(
                    missing_chil_rule.analyze(
                        record,
                        family_xref,
                        families,
                        child_families,
                    )
                )

        return issues