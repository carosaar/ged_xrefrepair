# /src/ged_xrefrepair/analyzer/rules/missing_husb.py

from ged_xrefrepair.model.issue import (
    Issue
)


class MissingHusbRule:

    def analyze(
        self,
        person_xref: str,
        family_xref: str,
        family_husb: dict,
        sex_map: dict,
    ) -> list[Issue]:

        #
        # Familie besitzt bereits
        # einen HUSB-Eintrag
        #

        if family_husb.get(
            family_xref
        ):
            return []

        #
        # Reparatur nur möglich,
        # wenn die Person männlich ist
        #

        auto_repair = (
            sex_map.get(
                person_xref
            ) == "M"
        )

        return [

            Issue(

                issue_type=
                    "MISSING_HUSB",

                #
                # Fehler befindet sich
                # im Familiendatensatz
                #

                record_id=
                    family_xref,

                #
                # Korrespondierende Person
                #

                related_xref=
                    person_xref,

                description=(

                    f"{person_xref} verweist "
                    f"auf {family_xref}, "
                    f"aber HUSB fehlt."

                ),

                auto_repair_possible=
                    auto_repair,
            )
        ]