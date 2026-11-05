# src/ged_xrefrepair/services/name_resolver.py

class NameResolver:

    def __init__(self, records):

        self.person_names = {}
        self.family_names = {}

        self._build_persons(records)
        self._build_families(records)

    
    def _build_persons(self, records):

        for record in records:

            if record.tag != "INDI":
                continue

            name = "<ohne Namen>"
            birth_date = ""
            death_date = ""

            in_birth = False
            in_death = False

            for line in record.lines:

                if line.startswith("1 NAME "):

                    name = (
                        line[7:]
                        .replace("/", "")
                        .strip()
                    )

                elif line.startswith("1 BIRT"):

                    in_birth = True
                    in_death = False

                elif line.startswith("1 DEAT"):

                    in_death = True
                    in_birth = False

                elif line.startswith("1 "):

                    in_birth = False
                    in_death = False

                elif (
                    in_birth
                    and line.startswith("2 DATE ")
                ):

                    birth_date = line[7:].strip()

                elif (
                    in_death
                    and line.startswith("2 DATE ")
                ):

                    death_date = line[7:].strip()

            dates = []

            if birth_date:
                dates.append(f"*{birth_date}")

            if death_date:
                dates.append(f"✝{death_date}")

            display_name = name

            if dates:
                display_name += (
                    " ("
                    + " ".join(dates)
                    + ")"
                )

            self.person_names[
                record.xref
            ] = display_name
    
    def _build_families(self, records):

        for record in records:

            if record.tag != "FAM":
                continue

            husb = None
            wife = None

            for line in record.lines:

                if line.startswith("1 HUSB "):
                    husb = line[7:].strip()

                elif line.startswith("1 WIFE "):
                    wife = line[7:].strip()

            husb_name = self._resolve_person_ref(husb)
            wife_name = self._resolve_person_ref(wife)

            self.family_names[
                record.xref
            ] = f"{husb_name} \n& \n{wife_name}"

    def resolve(self, xref: str) -> str:

        if xref.startswith("@I"):
            return self.person_names.get(
                xref,
                xref
            )

        if xref.startswith("@F"):
            return self.family_names.get(
                xref,
                xref
            )

        return xref
    
    def _resolve_person_ref(self, xref: str | None) -> str:

        if not xref:
            return "[kein Verweis]"

        if xref not in self.person_names:
            return f"{xref} [Person nicht vorhanden]"

        return self.person_names[xref]