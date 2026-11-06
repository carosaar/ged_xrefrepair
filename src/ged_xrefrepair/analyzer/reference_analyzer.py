# /src/ged_xrefrepair/analyzer/reference_analyzer.py

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

from ged_xrefrepair.analyzer.rules.missing_husb import (
    MissingHusbRule
)

from ged_xrefrepair.analyzer.rules.missing_wife import (
    MissingWifeRule
)

from ged_xrefrepair.analyzer.rules.missing_fams_husb import (
    MissingFamsHusbRule
)

from ged_xrefrepair.analyzer.rules.missing_fams_wife import (
    MissingFamsWifeRule
)

from ged_xrefrepair.model.issue import Issue
from ged_xrefrepair.model.gedcom_record import (
    GedcomRecord
)


class ReferenceAnalyzer:

    famc_pattern = re.compile(
        r"1 FAMC (@[^@]+@)"
    )

    pedi_pattern = re.compile(
        r"2 PEDI(?:\s+(.*))?$"
    )

    fams_pattern = re.compile(
        r"1 FAMS (@[^@]+@)"
    )

    chil_pattern = re.compile(
        r"1 CHIL (@[^@]+@)"
    )

    husb_pattern = re.compile(
        r"1 HUSB (@[^@]+@)"
    )

    wife_pattern = re.compile(
        r"1 WIFE (@[^@]+@)"
    )

    sex_pattern = re.compile(
        r"1 SEX ([MF])"
    )

    def analyze(
        self,
        records: list[GedcomRecord]
    ) -> list[Issue]:

        issues = []

        missing_family_rule = (
            MissingFamilyRule()
        )

        missing_chil_rule = (
            MissingChilRule()
        )

        missing_famc_rule = (
            MissingFamcRule()
        )

        multiple_famc_rule = (
            MultipleFamcRule()
        )

        missing_husb_rule = (
            MissingHusbRule()
        )
        
        missing_wife_rule = (
            MissingWifeRule()
        )

        missing_fams_husb_rule = (
            MissingFamsHusbRule()
        )

        missing_fams_wife_rule = (
            MissingFamsWifeRule()
        )

        families = {}

        child_families = {}

        person_families = {}

        birth_person_families = {}

        family_husb = {}

        family_wife = {}

        person_spouse_families = {}

        sex_map = {}

        #
        # Indizes aufbauen
        #

        for record in records:

            if record.tag == "FAM":

                children = set()

                husb = None

                wife = None

                for line in record.lines:

                    match = self.chil_pattern.match(
                        line
                    )

                    if match:

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

                    husb_match = (
                        self.husb_pattern.match(
                            line
                        )
                    )

                    if husb_match:

                        husb = (
                            husb_match.group(1)
                        )

                    wife_match = (
                        self.wife_pattern.match(
                            line
                        )
                    )

                    if wife_match:

                        wife = (
                            wife_match.group(1)
                        )

                families[
                    record.xref
                ] = children

                family_husb[
                    record.xref
                ] = husb

                family_wife[
                    record.xref
                ] = wife

            elif record.tag == "INDI":

                sex = None

                for line in record.lines:

                    famc_match = (
                        self.famc_pattern.match(
                            line
                        )
                    )

                    if famc_match:

                        family_xref = (
                            famc_match.group(1)
                        )

                        person_families.setdefault(
                            record.xref,
                            set()
                        ).add(
                            family_xref
                        )

                    fams_match = (
                        self.fams_pattern.match(
                            line
                        )
                    )

                    if fams_match:

                        family_xref = (
                            fams_match.group(1)
                        )

                        person_spouse_families.setdefault(
                            record.xref,
                            set()
                        ).add(
                            family_xref
                        )

                    sex_match = (
                        self.sex_pattern.match(
                            line
                        )
                    )

                    if sex_match:

                        sex = sex_match.group(1)

                birth_famc_refs = self._birth_famc_refs(
                    record.lines
                )
                if birth_famc_refs:
                    birth_person_families[
                        record.xref
                    ] = birth_famc_refs

                if sex:

                    sex_map[
                        record.xref
                    ] = sex

        #
        # MULTIPLE_FAMC
        #

        for (
            person_xref,
            families_set
        ) in birth_person_families.items():

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

        #
        # MISSING_FAMS_HUSB
        #

        for family_xref, husb_xref in (
            family_husb.items()
        ):

            if not husb_xref:
                continue

            issues.extend(
                missing_fams_husb_rule.analyze(
                    family_xref,
                    husb_xref,
                    person_spouse_families,
                    sex_map,
                )
            )
        
        #
        # MISSING_FAMS_WIFE
        #

        for family_xref, wife_xref in (
            family_wife.items()
        ):

            if not wife_xref:
                continue

            issues.extend(
                missing_fams_wife_rule.analyze(
                    family_xref,
                    wife_xref,
                    person_spouse_families,
                    sex_map,
                )
            )
        
        #
        # MISSING_HUSB
        #

        for (
            person_xref,
            family_set
        ) in person_spouse_families.items():

            for family_xref in family_set:

                issues.extend(
                    missing_husb_rule.analyze(
                        person_xref,
                        family_xref,
                        family_husb,
                        sex_map,
                    )
                )
        #
        # MISSING_WIFE
        #

        for (
            person_xref,
            family_set
        ) in person_spouse_families.items():

            for family_xref in family_set:

                issues.extend(
                    missing_wife_rule.analyze(
                        person_xref,
                        family_xref,
                        family_wife,
                        sex_map,
                    )
                )


        return issues

    def _birth_famc_refs(
        self,
        lines: list[str],
    ) -> set[str]:
        birth_famc_refs = set()
        line_index = 0

        while line_index < len(lines):
            famc_match = self.famc_pattern.match(
                lines[line_index]
            )
            if not famc_match:
                line_index += 1
                continue

            family_xref = famc_match.group(1)
            pedi_values = []
            line_index += 1

            while (
                line_index < len(lines)
                and not lines[line_index].startswith(("0 ", "1 "))
            ):
                pedi_match = self.pedi_pattern.match(
                    lines[line_index]
                )
                if pedi_match:
                    pedi_values.append(
                        (pedi_match.group(1) or "").strip()
                    )
                line_index += 1

            if not pedi_values or any(
                not pedi_value
                or pedi_value.upper() == "BIRTH"
                for pedi_value in pedi_values
            ):
                birth_famc_refs.add(family_xref)

        return birth_famc_refs
    
