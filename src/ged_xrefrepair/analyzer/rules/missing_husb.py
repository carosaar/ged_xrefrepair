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
        candidate_count: int = 1,
    ) -> list[Issue]:

        if family_husb.get(
            family_xref
        ):
            return []

        auto_repair = (
            sex_map.get(person_xref) == "M"
            and candidate_count == 1
        )

        ambiguity_note = (
            " Mehrere Personen mit SEX M verweisen auf diese Familie; "
            "die Zuordnung ist mehrdeutig."
            if candidate_count > 1
            else ""
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
                    f"{ambiguity_note}"
                ),

                auto_repair_possible=
                    auto_repair,
            )
        ]