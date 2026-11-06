from ged_xrefrepair.model.issue import (
    Issue
)


class MissingFamcRule:

    def analyze(
        self,
        family_xref,
        child_xref,
        person_families,
    ) -> list[Issue]:

        existing = (
            person_families.get(
                child_xref,
                set()
            )
        )

        if family_xref in existing:
            return []

        auto_repair = (
            len(existing) == 0
        )

        return [
            Issue(
                issue_type="MISSING_FAMC",

                record_id=child_xref,

                related_xref=family_xref,

                description=(
                    f"{family_xref} enthält "
                    f"{child_xref} als CHIL, "
                    f"aber FAMC fehlt."
                ),

                auto_repair_possible=
                    auto_repair,
            )
        ]