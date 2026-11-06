# /src/ged_xrefrepair/analyzer/rules/missing_husb.py

from ged_xrefrepair.model.issue import (
    Issue
)


class MissingHusbRule:

    def analyze(
        self,
        person_xref,
        family_xref,
        family_husb,
        sex_map,
    ) -> list[Issue]:

        if family_husb.get(
            family_xref
        ):
            return []

        auto_repair = (
            sex_map.get(
                person_xref
            ) == "M"
        )

        return [
            Issue(
                issue_type="MISSING_HUSB",

                record_id=family_xref,

                related_xref=person_xref,

                description=(
                    f"{person_xref} verweist "
                    f"auf {family_xref}, "
                    f"aber HUSB fehlt."
                ),

                auto_repair_possible=
                    auto_repair,
            )
        ]