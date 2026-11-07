# GED XRef Repair

GED XRef Repair ist ein Desktop-Werkzeug zur Analyse und selektiven Reparatur genealogischer GEDCOM-Dateien.

Ziel des Projekts ist das Erkennen und selektive Reparieren inkonsistenter
Referenzen zwischen Personen- und Familiendatensätzen.

Die Anwendung richtet sich an Familienforscher, Genealogen und Entwickler von GEDCOM-Werkzeugen, die die Konsistenz genealogischer Beziehungen überprüfen möchten.

---

## Aktueller Funktionsumfang

### Analyse

Derzeit erkennt die Anwendung folgende Referenzprobleme:

- `MISSING_CHIL` – FAMC-Verweis ohne passenden CHIL-Verweis
- `MISSING_FAMC` – CHIL-Verweis ohne passenden FAMC-Verweis
- `MISSING_FAMILY` – FAMC-/FAMS-Verweis auf eine nicht vorhandene Familie
- `MISSING_HUSB` / `MISSING_WIFE` – FAMS-Verweis auf eine Familie ohne passende Partnerrolle
- `MISSING_FAMS_HUSB` / `MISSING_FAMS_WIFE` – HUSB-/WIFE-Eintrag ohne passenden FAMS-Verweis
- `MISSING_PERSON` – HUSB-/WIFE-/CHIL-Verweis auf eine nicht vorhandene Person

Ein HUSB-/WIFE-/CHIL-Verweis auf eine nicht vorhandene Person wird als
`MISSING_PERSON` gemeldet, nicht als fehlender FAMS-/FAMC-Rückverweis.
Verweist `FAMS` oder `FAMC` auf eine nicht vorhandene Familie, wird
`MISSING_FAMILY` gemeldet und kein fehlender Gegenverweis abgeleitet.

`MISSING_CHIL` und `MISSING_FAMC` gleichen die FAMC- und CHIL-Verweise
familienbezogen ab, unabhängig von PEDI-Untertags und weiteren
Familienzuordnungen. Fehlt der referenzierte FAM- oder INDI-Datensatz, wird
stattdessen der nicht automatisch lösbare Problemtyp `MISSING_FAMILY`
beziehungsweise `MISSING_PERSON` gemeldet.

Wenn mehrere Personen mit passendem SEX über `FAMS` auf dieselbe Familie ohne
HUSB beziehungsweise WIFE verweisen, bleiben die einzelnen Kandidaten in der
Problemliste sichtbar. Ihre Zuordnung gilt als mehrdeutig und wird nicht zur
automatischen Reparatur vorgeschlagen. Eine automatische Zuordnung setzt einen
einzigen passenden Kandidaten voraus.

Mehrere `FAMC`-Verweise werden nicht als eigener Problemfall gemeldet. Die
PEDI-Klassifikation (z. B. Abstammung, `ADOPTED` oder `FOSTER`) wird nicht zur
Erzeugung eines `MULTIPLE_FAMC`-Befunds verwendet. Andere Prüfungen auf
fehlende oder widersprüchliche FAMC-/CHIL-Referenzen bleiben davon unberührt.

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
- Filter nach Problemtyp und Reparierbarkeit; beide Filter können kombiniert werden
- Alle auswählen
- Keine auswählen
- Auswahl umkehren

Die Auswahlaktionen wirken nur auf die aktuell gefilterten und sichtbaren
Probleme. Ausgeblendete Probleme behalten ihren Auswahlstatus.

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

### Problemübersicht

Über **❓ HILFE** wird ein eigenständiges, nicht-modales Fenster mit den
erkannten Problemtypen und ihren Bedingungen für eine eindeutige Lösung
geöffnet. Das Fenster kann neben dem Hauptfenster geöffnet bleiben und wird
beim Beenden der Anwendung geschlossen. Die Übersicht erläutert die
Reparierbarkeit; Reparaturen werden über die markierten Einträge im
Hauptfenster angewendet.

### Reparieren und speichern

Markieren Sie die zu reparierenden, als automatisch reparierbar eingestuften
Probleme und wählen Sie **🛠 Reparieren**. Die Änderungen werden zunächst nur
auf die Datensätze im Arbeitsspeicher angewendet; die Originaldatei bleibt
unverändert. **💾 Speichern...** schreibt die geänderten Datensätze in eine
separate GEDCOM-Datei. Ein Überschreiben der gerade analysierten Quelldatei
wird verhindert. Vor dem Speichern wird eine Sicherungskopie der geladenen
Quelldatei unter `<datei>.bak` erstellt; eine vorhandene Sicherung wird
überschrieben. Mit **↶ Rückgängig** lässt sich jede Reparaturrunde vollständig
zurücknehmen.

### Datei öffnen

Über:

```text
📂 Öffnen
```

eine GEDCOM-Datei auswählen.

Nach dem Öffnen wird die Analyse automatisch gestartet.

Die Analyse läuft in einem Hintergrundthread, sodass das Fenster währenddessen
reagiert. Die Statusleiste zeigt „Analyse läuft...“ und nach Abschluss eine
Erfolg- oder Fehlermeldung. Eine Fortschrittsanzeige wird nicht verwendet.
Währenddessen sind „Öffnen“ und „Analysieren“ deaktiviert, damit keine zweite
Analyse parallel gestartet und die Eingabedatei nicht gewechselt wird.

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
