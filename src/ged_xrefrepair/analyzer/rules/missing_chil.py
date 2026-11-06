from ged_xrefrepair.model.issue import Issue


class MissingChilRule:

    def analyze(
        self,
        record,
        family_xref,
        families,
        child_families,
    ) -> list[Issue]:

        if record.xref in families[family_xref]:
            return []

        auto_repair = True

        other_families = (
            child_families.get(
                record.xref,
                set()
            )
            - {family_xref}
        )

        if other_families:
            auto_repair = False

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

                auto_repair_possible=auto_repair,
            )
        ]