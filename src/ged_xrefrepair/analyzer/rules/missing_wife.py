# /src/ged_xrefrepair/analyzer/rules/missing_wife.py

from ged_xrefrepair.model.issue import (
    Issue
)


class MissingWifeRule:

    def analyze(
        self,
        person_xref: str,
        family_xref: str,
        family_wife: dict,
        sex_map: dict,
        candidate_count: int = 1,
    ) -> list[Issue]:

        #
        # Familie besitzt bereits
        # einen WIFE-Eintrag
        #

        if family_wife.get(
            family_xref
        ):
            return []

        #
        # Reparatur nur möglich,
        # wenn die Person weiblich ist
        #

        auto_repair = (
            sex_map.get(
                person_xref
            ) == "F"
            and candidate_count == 1
        )

        ambiguity_note = (
            " Mehrere Personen mit SEX F verweisen auf diese Familie; "
            "die Zuordnung ist mehrdeutig."
            if candidate_count > 1
            else ""
        )

        return [
            Issue(
                issue_type="MISSING_WIFE",

                record_id=family_xref,

                related_xref=person_xref,

                description=(
                    f"{person_xref} verweist "
                    f"auf {family_xref}, "
                    f"aber WIFE fehlt."
                    f"{ambiguity_note}"
                ),

                auto_repair_possible=
                    auto_repair,
            )
        ]