# Repair Rules

Dieses Dokument beschreibt die fachlichen Regeln zur Erkennung und automatischen Reparatur von Referenzfehlern in GEDCOM-Dateien.

Grundsatz:

Eine automatische Reparatur ist nur dann zulässig, wenn die fehlende Information eindeutig aus bereits vorhandenen Daten abgeleitet werden kann.

Sobald mehrere mögliche Interpretationen existieren oder Informationen fehlen oder in sich widersprüchlich sind, darf keine automatische Reparatur erfolgen.

---

# 1. MISSING_CHIL

## 1.1. Beschreibung

Eine Person verweist über einen FAMC-Eintrag auf eine Familie, die Familie enthält jedoch keinen passenden CHIL-Eintrag.

Beispiel:

Person:

```gedcom
0 @I1@ INDI
1 FAMC @F1@
```

Familie:

```gedcom
0 @F1@ FAM
```

Fehlend:

```gedcom
1 CHIL @I1@
```

## 1.2. Voraussetzung

Vorhanden:

```gedcom
INDI.FAMC -> FAM
```

Der referenzierte Familiendatensatz existiert.

Der passende CHIL-Eintrag fehlt 
und es gibt insgesamt keinen entsprechenden CHIL-Eintrag in einem anderen Familiendatensatz.
**Anmerkung zur Logikvereinfachung**: Ein Kind darf nur einer Elternfamilie zugeordnet sein.


## 1.3. Automatische Reparatur möglich

JA, wenn:

- der referenzierte FAM-Datensatz existiert UND
- kein passender CHIL-Eintrag vorhanden ist UND
- das Kind nicht bereits als CHIL in einem anderen FAM-Datensatz eingetragen ist

## 1.4. Automatische Reparatur nicht möglich

NEIN, wenn:

- der FAM-Datensatz fehlt ODER
- das Kind bereits als CHIL in einer anderen Familie vorkommt ODER
- die Beziehung dadurch mehrdeutig wird

---

## 1.5.Reparaturaktion

Einfügen in den Familiendatensatz:

```gedcom
1 CHIL @Ix@
```

---

# 2. MISSING_FAMC

## 2.1. Beschreibung

Eine Familie enthält einen CHIL-Eintrag, die Person besitzt jedoch keinen passenden FAMC-Eintrag.

Beispiel:

Familie:

```gedcom
0 @F1@ FAM
1 CHIL @I1@
```

Person:

```gedcom
0 @I1@ INDI
```

Fehlend:

```gedcom
1 FAMC @F1@
```

## 2.2. Voraussetzung

Vorhanden:

```gedcom
FAM.CHIL -> INDI
```

Der referenzierte Personendatensatz existiert.


## 2.3. Automatische Reparatur möglich

JA, wenn:

- der INDI-Datensatz existiert UND
- kein passender FAMC-Eintrag vorhanden ist UND
- kein anderer FAMC-Eintrag im Personendatensatz existiert


## 2.4. Automatische Reparatur nicht möglich

NEIN, wenn:

- der Personendatensatz fehlt ODER
- bereits ein anderer FAMC-Eintrag vorhanden ist wodurch mehrdeutige Elternbeziehungen entstehen würden

## 2.5. Reparaturaktion

Einfügen in den Personendatensatz:

```gedcom
1 FAMC @Fx@
```

---

# 3. MISSING_HUSB

## 3.1. Beschreibung

Eine Person verweist über FAMS auf eine Familie, die Familie enthält jedoch keinen passenden HUSB-Eintrag.

Beispiel:

Person:

```gedcom
0 @I1@ INDI
1 SEX M
1 FAMS @F1@
```

Familie:

```gedcom
0 @F1@ FAM
```

Fehlend:

```gedcom
1 HUSB @I1@
```

## 3.2. Voraussetzung

Vorhanden:

```gedcom
INDI.FAMS -> FAM
```

Der referenzierte Familiendatensatz existiert.

Gibt es mehrere Personen mit `SEX M`, die über `FAMS` auf dieselbe Familie
verweisen, sind sie mehrere mögliche Kandidaten. Alle Kandidaten werden
angezeigt; keiner davon ist automatisch reparierbar.

## 3.3. Automatische Reparatur möglich

JA, wenn:

- der FAM-Datensatz existiert UND
- kein HUSB-Eintrag vorhanden ist UND
- die Person existiert UND
- das SEX-Tag den Wert `1 SEX M` enthält
- genau eine Person mit `SEX M` über `FAMS` auf diese Familie verweist

## 3.4. Automatische Reparatur nicht möglich

NEIN, wenn:

- SEX fehlt ODER
- SEX nicht `M` ist ODER
- mehrere passende Personen als HUSB-Kandidat infrage kommen ODER
- bereits ein HUSB-Eintrag vorhanden ist ODER
- der Familiendatensatz fehlt

## 3.5. Reparaturaktion

Einfügen in den Familiendatensatz:

```gedcom
1 HUSB @Ix@
```

---

# 4. MISSING_WIFE

## 4.1. Beschreibung

Eine Person verweist über FAMS auf eine Familie, die Familie enthält jedoch keinen passenden WIFE-Eintrag.

Beispiel:

Person:

```gedcom
0 @I1@ INDI
1 SEX F
1 FAMS @F1@
```

Familie:

```gedcom
0 @F1@ FAM
```

Fehlend:

```gedcom
1 WIFE @I1@
```

## 4.2. Voraussetzung

Vorhanden:

```gedcom
INDI.FAMS -> FAM
```

Der referenzierte Familiendatensatz existiert.

Gibt es mehrere Personen mit `SEX F`, die über `FAMS` auf dieselbe Familie
verweisen, sind sie mehrere mögliche Kandidaten. Alle Kandidaten werden
angezeigt; keiner davon ist automatisch reparierbar.

## 4.3. Automatische Reparatur möglich

JA, wenn:

- der FAM-Datensatz existiert UND
- kein WIFE-Eintrag vorhanden ist UND
- die Person existiert UND
- das SEX-Tag den Wert `1 SEX F` enthält
- genau eine Person mit `SEX F` über `FAMS` auf diese Familie verweist

## 4.4. Automatische Reparatur nicht möglich

NEIN, wenn:

- SEX fehlt ODER
- SEX nicht `F` ist ODER
- mehrere passende Personen als WIFE-Kandidat infrage kommen ODER
- bereits ein WIFE-Eintrag vorhanden ist ODER
- der Familiendatensatz fehlt

## 4.5. Reparaturaktion

Einfügen in den Familiendatensatz:

```gedcom
1 WIFE @Ix@
```

# 5. MISSING_FAMS

Ein fehlender FAMS-Eintrag besitzt zwei Varianten.

## 5.1. MISSING_FAMS_HUSB

### 5.1.1. Beschreibung

Ein Familiendatensatz enthält einen HUSB-Eintrag, die Person besitzt jedoch keinen passenden FAMS-Eintrag.

Beispiel:

Familie:

```gedcom
0 @F1@ FAM
1 HUSB @I1@
```

Person:

```gedcom
0 @I1@ INDI
1 SEX M
```

Fehlend:

```gedcom
1 FAMS @F1@
```

### 5.1.2. Automatische Reparatur möglich

JA, wenn:

- der INDI-Datensatz existiert UND
- das SEX-Tag den Wert `M` besitzt UND
- kein passender FAMS-Eintrag vorhanden ist

### 5.1.3. Automatische Reparatur nicht möglich

NEIN, wenn:

- der Personendatensatz fehlt ODER
- SEX fehlt ODER
- SEX nicht `M` ist

### 5.1.4. Reparaturaktion

Einfügen in den Personendatensatz:

```gedcom
1 FAMS @Fx@
```

---

## 5.2. MISSING_FAMS_WIFE

### 5.2.1. Beschreibung

Ein Familiendatensatz enthält einen WIFE-Eintrag, die Person besitzt jedoch keinen passenden FAMS-Eintrag.

Beispiel:

Familie:

```gedcom
0 @F1@ FAM
1 WIFE @I1@
```

Person:

```gedcom
0 @I1@ INDI
1 SEX F
```

Fehlend:

```gedcom
1 FAMS @F1@
```

### 5.2.2. Automatische Reparatur möglich

JA, wenn:

- der INDI-Datensatz existiert UND
- das SEX-Tag den Wert `F` besitzt UND
- kein passender FAMS-Eintrag vorhanden ist

### 5.2.3. Automatische Reparatur nicht möglich

NEIN, wenn:

- der Personendatensatz fehlt ODER
- SEX fehlt ODER
- SEX nicht `F` ist

### 5.2.4. Reparaturaktion

Einfügen in den Personendatensatz:

```gedcom
1 FAMS @Fx@
```

---

# 6. MISSING_PERSON

## 6.1. Beschreibung

Ein HUSB- oder WIFE-Eintrag in einem Familiendatensatz verweist auf eine
Person, für die kein INDI-Datensatz existiert.

Der Befund wird als `MISSING_PERSON` gemeldet. Er wird nicht als fehlender
FAMS-Rückverweis klassifiziert, da eine nicht vorhandene Person keinen
FAMS-Eintrag enthalten kann.

---

# 7. MULTIPLE_FAMC

## 7.1. Beschreibung

Eine Person hat mehrere Abstammungszuordnungen über `FAMC`. Als Abstammungszuordnung
zählen nur FAMC-Verweise ohne `PEDI`-Untertag oder mit leerem `PEDI`-Wert bzw.
`PEDI BIRTH`.

FAMC-Verweise mit anderen `PEDI`-Werten, zum Beispiel `ADOPTED` oder `FOSTER`,
werden für diese Regel nicht als Abstammungszuordnung gezählt.

## 7.2. Erkennung

`MULTIPLE_FAMC` wird nur gemeldet, wenn mindestens zwei unterschiedliche
Abstammungsfamilien auf diese Weise zugeordnet sind. Die Regel nimmt keine
automatische Änderung vor; mögliche Zuordnungen müssen fachlich geprüft werden.

Beispiel:

```gedcom
0 @I1@ INDI
1 FAMC @F1@
1 FAMC @F2@
2 PEDI ADOPTED
```

In diesem Beispiel zählt nur `@F1@` als Abstammungsfamilie; `@F2@` ist durch
`PEDI ADOPTED` gekennzeichnet.

---

# 8. FAZIT
## 8.1. Grundregeln für automatische Reparaturen

Eine automatische Reparatur darf nur durchgeführt werden, wenn:

- alle beteiligten Datensätze existieren
- die einzufügende Information eindeutig ist
- keine widersprüchlichen Referenzen vorhanden sind
- keine bereits vorhandenen alternativen Beziehungen überschrieben werden


## 8.2. Nicht automatisch reparierbare Fälle

Die folgenden Fehlertypen gelten grundsätzlich als nicht automatisch reparierbar:

- Verweis auf nicht existierende Personen
- Verweis auf nicht existierende Familien
- Mehrdeutige Elternbeziehungen
- Mehrdeutige Partnerbeziehungen
- Fehlende Datensätze

In diesen Fällen darf GED XRef Repair lediglich einen Vorschlag anzeigen und muss die endgültige Entscheidung dem Benutzer überlassen.

---
---

# 9. Übersichtsmatrix

| Problemtyp | Beschreibung | Automatisch reparierbar | Voraussetzung |
|------------|-------------|-------------------------|---------------|
| MISSING_CHIL | FAMC vorhanden, CHIL fehlt | ✅ Ja | Familie existiert, kein CHIL vorhanden, keine konkurrierende Familie |
| MISSING_FAMC | CHIL vorhanden, FAMC fehlt | ✅ Ja | Person existiert, kein anderer FAMC-Eintrag vorhanden |
| MISSING_HUSB | FAMS vorhanden, HUSB fehlt | ✅ Ja | Familie existiert, genau ein Kandidat mit SEX=M, kein HUSB vorhanden |
| MISSING_WIFE | FAMS vorhanden, WIFE fehlt | ✅ Ja | Familie existiert, genau ein Kandidat mit SEX=F, kein WIFE vorhanden |
| MISSING_FAMS_HUSB | HUSB vorhanden, FAMS fehlt | ✅ Ja | Person existiert, SEX=M |
| MISSING_FAMS_WIFE | WIFE vorhanden, FAMS fehlt | ✅ Ja | Person existiert, SEX=F |
| MISSING_PERSON | Verweis auf nicht vorhandene Person | ❌ Nein | Zielperson fehlt |
| MISSING_FAMILY | Verweis auf nicht vorhandene Familie | ❌ Nein | Zielfamilie fehlt |
| MULTIPLE_FAMC | Mehrere Abstammungsfamilien (FAMC ohne PEDI oder PEDI leer/BIRTH) | ❌ Nein | Mindestens zwei unterschiedliche Abstammungsfamilien |
| MULTIPLE_HUSB | Mehrere mögliche Ehemänner | ❌ Nein | Fachliche Entscheidung erforderlich |
| MULTIPLE_WIFE | Mehrere mögliche Ehefrauen | ❌ Nein | Fachliche Entscheidung erforderlich |
| UNKNOWN_SEX | Geschlecht fehlt oder unbekannt | ❌ Nein | Rolle nicht eindeutig bestimmbar |
