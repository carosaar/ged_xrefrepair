# src/ged_xrefrepair/analyzer/rules/multiple_famc.py

from ged_xrefrepair.model.issue import (
    Issue
)


class MultipleFamcRule:

    def analyze(
        self,
        person_xref: str,
        families: set[str],
    ) -> list[Issue]:

        if len(families) <= 1:
            return []

        return [
            Issue(
                issue_type="MULTIPLE_FAMC",

                record_id=person_xref,

                related_xref=", ".join(
                    sorted(families)
                ),

                description=(
                    f"{person_xref} besitzt "
                    f"mehrere FAMC-Verweise: "
                    f"{', '.join(sorted(families))}"
                ),

                auto_repair_possible=False,
            )
        ]