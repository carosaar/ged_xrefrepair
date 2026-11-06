import re

from ged_xrefrepair.analyzer.rules.missing_family import (
    MissingFamilyRule
)

from ged_xrefrepair.analyzer.rules.missing_chil import (
    MissingChilRule
)

from ged_xrefrepair.analyzer.rules.missing_famc import (
    MissingFamcRule
)

from ged_xrefrepair.analyzer.rules.multiple_famc import (
    MultipleFamcRule
)

from ged_xrefrepair.model.issue import Issue
from ged_xrefrepair.model.gedcom_record import (
    GedcomRecord
)


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
        missing_famc_rule = MissingFamcRule()
        multiple_famc_rule = MultipleFamcRule()

        families = {}

        child_families = {}

        person_families = {}

        #
        # Indizes aufbauen
        #

        for record in records:

            #
            # Familienindex
            #

            if record.tag == "FAM":

                children = set()

                for line in record.lines:

                    match = (
                        self.chil_pattern.match(
                            line
                        )
                    )

                    if not match:
                        continue

                    child_xref = (
                        match.group(1)
                    )

                    children.add(
                        child_xref
                    )

                    child_families.setdefault(
                        child_xref,
                        set()
                    ).add(
                        record.xref
                    )

                families[
                    record.xref
                ] = children

            #
            # Personenindex
            #

            elif record.tag == "INDI":

                for line in record.lines:

                    match = (
                        self.famc_pattern.match(
                            line
                        )
                    )

                    if not match:
                        continue

                    family_xref = (
                        match.group(1)
                    )

                    person_families.setdefault(
                        record.xref,
                        set()
                    ).add(
                        family_xref
                    )

        #
        # MULTIPLE_FAMC
        #

        for person_xref, families_set in (
            person_families.items()
        ):

            issues.extend(
                multiple_famc_rule.analyze(
                    person_xref,
                    families_set,
                )
            )

        #
        # MISSING_FAMILY
        # MISSING_CHIL
        #

        for record in records:

            if record.tag != "INDI":
                continue

            for line in record.lines:

                match = (
                    self.famc_pattern.match(
                        line
                    )
                )

                if not match:
                    continue

                family_xref = (
                    match.group(1)
                )

                issues.extend(
                    missing_family_rule.analyze(
                        record,
                        family_xref,
                        families,
                    )
                )

                if family_xref not in families:
                    continue

                issues.extend(
                    missing_chil_rule.analyze(
                        record,
                        family_xref,
                        families,
                        child_families,
                    )
                )

        #
        # MISSING_FAMC
        #

        for record in records:

            if record.tag != "FAM":
                continue

            for line in record.lines:

                match = (
                    self.chil_pattern.match(
                        line
                    )
                )

                if not match:
                    continue

                child_xref = (
                    match.group(1)
                )

                issues.extend(
                    missing_famc_rule.analyze(
                        record.xref,
                        child_xref,
                        person_families,
                    )
                )
                
            
#######            
        return issues