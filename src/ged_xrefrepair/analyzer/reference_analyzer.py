import re

from ged_xrefrepair.model.issue import Issue
from ged_xrefrepair.model.gedcom_record import GedcomRecord


class ReferenceAnalyzer:

    famc_pattern = re.compile(
        r"1 FAMC (@[^@]+@)"
    )

    chil_pattern = re.compile(
        r"1 CHIL (@[^@]+@)"
    )

    def analyze(
        self,
        records: list[GedcomRecord]
    ) -> list[Issue]:

        issues = []

        families = {}

        for record in records:

            if record.tag != "FAM":
                continue

            children = set()

            for line in record.lines:

                match = self.chil_pattern.match(line)

                if match:
                    children.add(match.group(1))

            families[record.xref] = children

        for record in records:

            if record.tag != "INDI":
                continue

            for line in record.lines:

                match = self.famc_pattern.match(line)

                if not match:
                    continue

                family_xref = match.group(1)

                if family_xref not in families:
                    continue

                if record.xref not in families[family_xref]:

                    issues.append(
                        Issue(
                            issue_type="MISSING_CHIL",

                            # Familie enthält den Fehler
                            record_id=family_xref,

                            # korrespondierende Person
                            related_xref=record.xref,

                            description=(
                                f"{record.xref} verweist "
                                f"auf {family_xref}, "
                                "aber CHIL fehlt."
                            ),

                            auto_repair_possible=True
                        )
                    )
        return issues

