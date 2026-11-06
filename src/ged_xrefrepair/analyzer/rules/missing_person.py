from ged_xrefrepair.model.issue import Issue


class MissingPersonRule:

    def analyze(
        self,
        family_xref: str,
        person_xref: str,
        role: str,
        person_xrefs: set[str],
    ) -> list[Issue]:
        if person_xref in person_xrefs:
            return []

        return [
            Issue(
                issue_type="MISSING_PERSON",
                record_id=family_xref,
                related_xref=person_xref,
                description=(
                    f"{family_xref} verweist als {role} auf "
                    f"die nicht vorhandene Person {person_xref}."
                ),
                auto_repair_possible=False,
            )
        ]
