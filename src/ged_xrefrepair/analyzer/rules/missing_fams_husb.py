# /src/ged_xrefrepair/analyzer/rules/missing_fams_husb.py

from ged_xrefrepair.model.issue import (
    Issue
)


class MissingFamsHusbRule:

    def analyze(
        self,
        family_xref: str,
        person_xref: str,
        person_spouse_families: dict,
        sex_map: dict,
    ) -> list[Issue]:

        existing = (
            person_spouse_families.get(
                person_xref,
                set()
            )
        )

        if family_xref in existing:
            return []

        auto_repair = (
            sex_map.get(
                person_xref
            ) == "M"
        )

        return [
            Issue(
                issue_type=
                    "MISSING_FAMS_HUSB",

                record_id=
                    person_xref,

                related_xref=
                    family_xref,

                description=(
                    f"{family_xref} enthält "
                    f"{person_xref} als HUSB, "
                    f"aber FAMS fehlt."
                ),

                auto_repair_possible=
                    auto_repair,
            )
        ]