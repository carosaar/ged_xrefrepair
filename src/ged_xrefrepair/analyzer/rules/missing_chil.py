from ged_xrefrepair.model.issue import Issue


class MissingChilRule:

    def analyze(
        self,
        record,
        family_xref,
        families,
    ) -> list[Issue]:

        if record.xref in families[family_xref]:
            return []

        return [
            Issue(
                issue_type="MISSING_CHIL",

                record_id=family_xref,

                related_xref=record.xref,

                description=(
                    f"{record.xref} verweist "
                    f"auf {family_xref}, "
                    f"aber CHIL fehlt."
                ),

                auto_repair_possible=True,
            )
        ]