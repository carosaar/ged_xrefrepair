# /src/ged_xrefrepair/analyzer/reference_analyzer.py

import re

from ged_xrefrepair.analyzer.rules.missing_family import (
    MissingFamilyRule
)

from ged_xrefrepair.analyzer.rules.missing_person import (
    MissingPersonRule
)

from ged_xrefrepair.analyzer.rules.missing_chil import (
    MissingChilRule
)

from ged_xrefrepair.analyzer.rules.missing_famc import (
    MissingFamcRule
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

        missing_person_rule = (
            MissingPersonRule()
        )

        missing_chil_rule = (
            MissingChilRule()
        )

        missing_famc_rule = (
            MissingFamcRule()
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

        person_families = {}

        family_husb = {}

        family_wife = {}

        person_spouse_families = {}

        sex_map = {}
        person_xrefs = {
            record.xref
            for record in records
            if record.tag == "INDI"
        }

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

                if sex:

                    sex_map[
                        record.xref
                    ] = sex

        #
        # MISSING_FAMILY
        # MISSING_CHIL
        #

        checked_child_relations = set()

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

                relation = (record.xref, family_xref)
                if relation in checked_child_relations:
                    continue
                checked_child_relations.add(relation)

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
                    )
                )

        #
        # MISSING_FAMC
        #

        checked_child_relations = set()

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

                relation = (record.xref, child_xref)
                if relation in checked_child_relations:
                    continue
                checked_child_relations.add(relation)

                if child_xref not in person_xrefs:
                    issues.extend(
                        missing_person_rule.analyze(
                            record.xref,
                            child_xref,
                            "CHIL",
                            person_xrefs,
                        )
                    )
                    continue

                issues.extend(
                    missing_famc_rule.analyze(
                        record.xref,
                        child_xref,
                        person_families,
                    )
                )

        #
        # MISSING_FAMILY über FAMS
        #

        for record in records:

            if record.tag != "INDI":
                continue

            for line in record.lines:

                match = self.fams_pattern.match(line)
                if not match:
                    continue

                issues.extend(
                    missing_family_rule.analyze(
                        record,
                        match.group(1),
                        families,
                    )
                )

        #
        # MISSING_PERSON über HUSB/WIFE
        #

        for family_xref, person_xref in family_husb.items():
            if person_xref:
                issues.extend(
                    missing_person_rule.analyze(
                        family_xref,
                        person_xref,
                        "HUSB",
                        person_xrefs,
                    )
                )

        for family_xref, person_xref in family_wife.items():
            if person_xref:
                issues.extend(
                    missing_person_rule.analyze(
                        family_xref,
                        person_xref,
                        "WIFE",
                        person_xrefs,
                    )
                )

        #
        # MISSING_FAMS_HUSB
        #

        husb_candidate_counts = {}
        wife_candidate_counts = {}

        for person_xref, family_set in person_spouse_families.items():
            for family_xref in family_set:
                if family_xref not in families:
                    continue

                if (
                    not family_husb.get(family_xref)
                    and sex_map.get(person_xref) == "M"
                ):
                    husb_candidate_counts[family_xref] = (
                        husb_candidate_counts.get(family_xref, 0) + 1
                    )

                if (
                    not family_wife.get(family_xref)
                    and sex_map.get(person_xref) == "F"
                ):
                    wife_candidate_counts[family_xref] = (
                        wife_candidate_counts.get(family_xref, 0) + 1
                    )

        for family_xref, husb_xref in (
            family_husb.items()
        ):

            if not husb_xref:
                continue

            if husb_xref not in person_xrefs:
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

            if wife_xref not in person_xrefs:
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

                if family_xref not in families:
                    continue

                issues.extend(
                    missing_husb_rule.analyze(
                        person_xref,
                        family_xref,
                        family_husb,
                        sex_map,
                        husb_candidate_counts.get(family_xref, 0),
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

                if family_xref not in families:
                    continue

                issues.extend(
                    missing_wife_rule.analyze(
                        person_xref,
                        family_xref,
                        family_wife,
                        sex_map,
                        wife_candidate_counts.get(family_xref, 0),
                    )
                )


        return issues
