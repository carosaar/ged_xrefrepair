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

PEDI-Untertags beeinflussen diesen Abgleich nicht. Ein FAMC-Verweis auf die
konkrete Familie wird unabhängig davon geprüft, ob ein PEDI-Untertag fehlt,
leer ist oder beispielsweise `BIRTH`, `ADOPTED` oder `FOSTER` enthält.

Der referenzierte Familiendatensatz existiert.

Der passende CHIL-Eintrag fehlt. CHIL-Einträge in anderen Familiendatensätzen
beeinflussen diesen Befund nicht.


## 1.3. Automatische Reparatur möglich

JA, wenn:

- der referenzierte FAM-Datensatz existiert UND
- kein passender CHIL-Eintrag in genau dieser Familie vorhanden ist

## 1.4. Automatische Reparatur nicht möglich

NEIN, wenn:

- der FAM-Datensatz fehlt; dieser Fall wird als `MISSING_FAMILY` gemeldet

---

## 1.5. Reparaturaktion

Einfügen in den Familiendatensatz:

```gedcom
1 CHIL @Ix@
```

---

# 2. MISSING_FAMC

## 2.1. Beschreibung

Eine Familie enthält einen CHIL-Eintrag, die Person besitzt jedoch keinen passenden FAMC-Eintrag.

PEDI-Untertags und FAMC-Verweise auf andere Familien beeinflussen den Abgleich
nicht. Als vorhandener Gegenverweis zählt ein FAMC auf genau die CHIL-Familie,
unabhängig davon, ob ein PEDI-Untertag fehlt, leer ist oder beispielsweise
`BIRTH`, `ADOPTED` oder `FOSTER` enthält.

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
- kein FAMC-Eintrag auf genau diese Familie vorhanden ist


## 2.4. Automatische Reparatur nicht möglich

NEIN, wenn:

- der Personendatensatz fehlt; dieser Fall wird als `MISSING_PERSON` gemeldet

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

Ein HUSB-, WIFE- oder CHIL-Eintrag in einem Familiendatensatz verweist auf
eine Person, für die kein INDI-Datensatz existiert.

Der Befund wird als `MISSING_PERSON` gemeldet. Er wird nicht als fehlender
FAMS- oder FAMC-Rückverweis klassifiziert, da eine nicht vorhandene Person
keinen INDI-Datensatz mit einem solchen Eintrag enthalten kann.

---

# 7. Mehrere FAMC-Verweise

Mehrere FAMC-Verweise werden nicht als eigener Problemfall (`MULTIPLE_FAMC`)
gemeldet. Die Anwendung bewertet nicht, ob die FAMC-Verweise unterschiedliche
Abstammungs-, Adoptiv- oder Pflegebeziehungen beschreiben. Insbesondere werden
`PEDI`-Werte wie `ADOPTED` und `FOSTER` nicht für einen
`MULTIPLE_FAMC`-Befund ausgewertet.

Andere Referenzprüfungen, etwa auf fehlende oder widersprüchliche FAMC-/CHIL-
Verweise, bleiben davon unberührt.

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
| MISSING_CHIL | FAMC vorhanden, passender CHIL fehlt | ✅ Ja | Person und referenzierte Familie existieren |
| MISSING_FAMC | CHIL vorhanden, passender FAMC fehlt | ✅ Ja | Familie und referenzierte Person existieren |
| MISSING_HUSB | FAMS vorhanden, HUSB fehlt | ✅ Ja | Familie existiert, genau ein Kandidat mit SEX=M, kein HUSB vorhanden |
| MISSING_WIFE | FAMS vorhanden, WIFE fehlt | ✅ Ja | Familie existiert, genau ein Kandidat mit SEX=F, kein WIFE vorhanden |
| MISSING_FAMS_HUSB | HUSB vorhanden, FAMS fehlt | ✅ Ja | Person existiert, SEX=M |
| MISSING_FAMS_WIFE | WIFE vorhanden, FAMS fehlt | ✅ Ja | Person existiert, SEX=F |
| MISSING_PERSON | HUSB-/WIFE-/CHIL-Verweis auf nicht vorhandene Person | ❌ Nein | Zielperson fehlt |
| MISSING_FAMILY | Verweis auf nicht vorhandene Familie | ❌ Nein | Zielfamilie fehlt |

Fehlendes oder widersprüchliches Geschlecht sowie mehrere mögliche HUSB- oder
WIFE-Kandidaten werden als nicht automatisch reparierbare `MISSING_HUSB`- bzw.
`MISSING_WIFE`-Befunde angezeigt; dafür gibt es keine separaten Problemtypen.

Die Einstufung „automatisch reparierbar“ beschreibt, ob die fehlende Referenz
aus Sicht der Analyse eindeutig ergänzt werden kann. Nur ausgewählte Befunde
mit dieser Einstufung werden im Arbeitsspeicher repariert. Die Originaldatei
wird nicht überschrieben; geänderte Datensätze können in eine separate
GEDCOM-Datei gespeichert werden. Jede Reparaturrunde kann vollständig
rückgängig gemacht werden. Vor dem Speichern wird eine Sicherungskopie der
geladenen Originaldatei mit der Endung `.bak` erstellt und eine vorhandene
Sicherung überschrieben. Prüfen Sie alle Befunde anhand Ihrer Quelldaten.
