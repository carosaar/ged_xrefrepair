# GED XRef Repair

GED XRef Repair ist ein Desktop-Werkzeug zur Analyse genealogischer GEDCOM-Dateien.

Ziel des Projekts ist das Erkennen und spätere automatische Reparieren inkonsistenter Referenzen zwischen Personen- und Familiendatensätzen.

Die Anwendung richtet sich an Familienforscher, Genealogen und Entwickler von GEDCOM-Werkzeugen, die die Konsistenz genealogischer Beziehungen überprüfen möchten.

---

## Aktueller Funktionsumfang

### Analyse

Derzeit erkennt die Anwendung folgende Referenzprobleme:

- `MISSING_CHIL` – FAMC-Verweis ohne passenden CHIL-Verweis
- `MISSING_FAMC` – CHIL-Verweis ohne passenden FAMC-Verweis
- `MISSING_FAMILY` – Verweis auf eine nicht vorhandene Familie
- `MISSING_HUSB` / `MISSING_WIFE` – FAMS-Verweis auf eine Familie ohne passende Partnerrolle
- `MISSING_FAMS_HUSB` / `MISSING_FAMS_WIFE` – HUSB-/WIFE-Eintrag ohne passenden FAMS-Verweis
- `MULTIPLE_FAMC` – mehrere Abstammungsfamilien für eine Person

`MULTIPLE_FAMC` berücksichtigt nur FAMC-Verweise ohne `PEDI`-Untertag oder
mit leerem `PEDI`-Wert beziehungsweise `PEDI BIRTH`. Verweise mit anderen
PEDI-Werten, zum Beispiel `ADOPTED` oder `FOSTER`, zählen nicht als
Abstammungszuordnung. Ein Hinweis wird ausgegeben, wenn mindestens zwei
unterschiedliche Abstammungsfamilien vorliegen. Daraus wird keine automatische
Reparatur abgeleitet.

Beispiel für einen FAMC-Verweis, der wegen `PEDI ADOPTED` nicht als
Abstammungszuordnung gezählt wird:

```gedcom
0 @I1@ INDI
1 FAMC @F1@
1 FAMC @F2@
2 PEDI ADOPTED
```

Hier zählt `@F1@` als Abstammungsfamilie; `@F2@` ist durch `PEDI ADOPTED`
gekennzeichnet und wird von `MULTIPLE_FAMC` nicht mitgezählt.

---

### Problemliste

Gefundene Probleme werden in einer Tabelle dargestellt.

Für jedes Problem werden angezeigt:

- Datensatz
- Problemtyp
- Beschreibung
- Reparierbarkeit

Funktionen:

- Sortierung über Spaltenüberschriften
- Alle auswählen
- Keine auswählen
- Auswahl umkehren

---

### Detailansicht

Für den ausgewählten Problemfall werden ausführliche Informationen angezeigt:

- Problemtyp
- Problemdatensatz
- Korrespondierender Datensatz
- Beschreibung

GEDCOM-XREFs werden dabei in genealogisch lesbare Informationen aufgelöst.

---

### Namensauflösung

#### Personen

Personen werden dargestellt als:

```text
Max Mustermann (*12 MAR 1887 ✝15 SEP 1951)
```

Verwendete Informationen:

- Name
- Geburtsdatum (falls vorhanden)
- Sterbedatum (falls vorhanden)

#### Familien

Familien werden dargestellt als:

```text
Max Mustermann (*1887 ✝1951)
⚭ 10 MAY 1910
Erika Schmidt (*1890 ✝1965)
```

Verwendete Informationen:

- Ehemann
- Ehefrau
- Heiratsdatum

Falls mehrere Heiratsereignisse vorhanden sind, wird bevorzugt ein Ereignis vom Typ:

```text
CIVIL
```

verwendet.

Existiert kein solches Ereignis, wird der erste gefundene Heiratseintrag verwendet.

---

### Fehlerkennzeichnung

Nicht auflösbare Referenzen werden explizit dargestellt.

Beispiele:

```text
@I10@ [Person nicht vorhanden]
```

```text
[kein HUSB]
```

```text
[kein WIFE]
```

---

## Bedienung

### Datei öffnen

Über:

```text
📂 Öffnen
```

eine GEDCOM-Datei auswählen.

Nach dem Öffnen wird die Analyse automatisch gestartet.

Die Anwendung liest GEDCOM-Dateien derzeit als UTF-8. Kann eine Datei nicht
geöffnet oder gelesen werden oder ist sie nicht gültig UTF-8-kodiert, erscheint
eine Fehlermeldung. Ergebnisse einer vorherigen Datei werden beim Start einer
neuen Analyse verworfen und bei einem Fehler nicht weiter angezeigt.

### Letzte Datei

Die zuletzt verwendete GEDCOM-Datei wird gespeichert.

Beim nächsten Programmstart wird:

- Dateiname
- Dateipfad

automatisch wiederhergestellt.

Die Analyse wird in diesem Fall bewusst nicht automatisch ausgeführt.

---

## Projektstruktur

```text
src/
└── ged_xrefrepair/
    ├── analyzer/
    ├── gui/
    ├── model/
    ├── parser/
    └── services/
```

Wichtige Komponenten:

| Modul | Aufgabe |
|---------|----------|
| parser | Einlesen der GEDCOM-Datei |
| analyzer | fachliche Konsistenzprüfungen |
| services | Analyse- und Namensauflösung |
| model | Datenmodelle |
| gui | Qt-Benutzeroberfläche |

---

## Entwicklung

### Voraussetzungen

- Python 3.12 oder neuer
- PySide6

Installation:

```bash
pip install -e .
```

oder

```bash
pip install -r requirements.txt
```

---

### Anwendung starten

Aus dem Projektverzeichnis:

```bash
python -m ged_xrefrepair
```

---

## Roadmap

### Geplant

- Reparaturvorschau
- Selektive Reparatur ausgewählter Probleme
- Unterstützung weiterer Referenzfehler

Geplante Fehlertypen:

- MISSING_FAMC
- MISSING_FAMS
- MISSING_HUSB
- MISSING_WIFE

---

## Lizenz

Derzeit keine Lizenz festgelegt.

---

## Status

Aktuelle Version:

```text
0.5.1
```

Projektstatus:

```text
Aktive Entwicklung
```

Der Schwerpunkt liegt aktuell auf der Erweiterung der Analysefunktionen und der Vorbereitung der automatischen Reparaturlogik.
