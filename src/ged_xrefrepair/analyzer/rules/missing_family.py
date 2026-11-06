from ged_xrefrepair.model.issue import Issue


class MissingFamilyRule:

    def analyze(
        self,
        record,
        family_xref,
        families,
    ) -> list[Issue]:

        if family_xref in families:
            return []

        return [
            Issue(
                issue_type="MISSING_FAMILY",

                record_id=record.xref,

                related_xref=family_xref,

                description=(
                    f"Verweis auf "
                    f"nicht vorhandene Familie "
                    f"{family_xref}"
                ),

                auto_repair_possible=False,
            )
        ]