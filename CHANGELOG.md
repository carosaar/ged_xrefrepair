# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

---

## [0.2.0] - Erkennung fehlender FAMC/CHIL-Referenzen
04.11.2026 05:00

### Hinzugefügt

- Erstes fachliches Analysemodul für genealogische Referenzen implementiert.
- Neues Issue-Modell eingeführt, um erkannte Probleme strukturiert beschreiben zu können.
- Analyseergebnis über die neue Klasse `AnalysisResult` vereinheitlicht.

### Referenzanalyse

Das Programm erkennt jetzt den Fall:

INDI:FAMC → Familie vorhanden,
aber
FAM:CHIL → Person fehlt.

Beispiel:

Person:

    1 FAMC @F1@

Familie:

    0 @F1@ FAM

ohne

    1 CHIL @I1@

Solche Inkonsistenzen werden als Problem vom Typ

    MISSING_CHIL

erfasst.

### Architektur

- Neues Modul `ReferenceAnalyzer` eingeführt.
- Analyse der Familien-Kind-Referenzen von der GUI entkoppelt.
- Grundlage für weitere Referenzregeln geschaffen.

### Qualitätssicherung

- Testdateien für fehlerhafte Familienreferenzen vorbereitet.
- Aufbau einer automatisierten Prüfbasis mit pytest begonnen.

### Benutzeroberfläche

- Die Analyse liefert jetzt zusätzlich die Anzahl erkannter Probleme.
- Vorbereitung für die spätere Anzeige einzelner Probleme in Tabellenform.

### Noch nicht enthalten

Dieser Meilenstein erkennt Probleme ausschließlich.

Es werden noch keine Veränderungen an der GEDCOM-Datei vorgenommen.

Automatische Reparaturen sind für einen späteren Entwicklungsschritt vorgesehen.

### Motivation

Mit diesem Release beginnt die eigentliche Kernfunktion des Projekts:

das Erkennen inkonsistenter genealogischer Beziehungen.

Die Reparaturlogik wird erst entwickelt, nachdem die Erkennung aller relevanten Problemtypen zuverlässig funktioniert.

---
## [0.1.0] - Initiale Projektstruktur und GEDCOM-Import
04.11.2026 04:00

### Hinzugefügt

- Grundlegende Projektstruktur als installierbares Python-Modul aufgebaut.
- Verwendung des modernen `src`-Layouts eingeführt.
- Unterstützung für virtuelle Python-Umgebungen (`.venv`) eingerichtet.
- Projektkonfiguration über `pyproject.toml` angelegt.
- Entwicklungsumgebung mit `pytest` vorbereitet.
- Qt-basierte Desktop-Anwendung mit PySide6 eingerichtet.

### Benutzeroberfläche

- Erstes Anwendungsfenster implementiert.
- Dateiauswahldialog zum Öffnen von GEDCOM-Dateien hinzugefügt.
- Analyse-Schaltfläche integriert.
- Statusleiste für Rückmeldungen an den Benutzer vorbereitet.

### GEDCOM-Verarbeitung

- Erste Version des GEDCOM-Parsers implementiert.
- Zerlegung einer GEDCOM-Datei in einzelne Datensätze (`GedcomRecord`) realisiert.
- Unterstützung für die Datensatztypen `INDI` und `FAM` vorbereitet.

### Analyse

- Zählung von Personen-Datensätzen (`INDI`) umgesetzt.
- Zählung von Familien-Datensätzen (`FAM`) umgesetzt.
- Gesamtanzahl aller Datensätze ermittelbar.

### Architektur

- Trennung zwischen GUI, Service-Layer, Parser und Datenmodell eingeführt.
- Grundlage für spätere Analyse- und Reparaturfunktionen vorbereitet.

### Motivation

Dieser Meilenstein stellt einen ersten vollständigen vertikalen Schnitt durch die Anwendung dar:

GEDCOM-Datei → Parser → Analyse-Service → GUI

Damit wurde die technische Basis für alle weiteren Entwicklungen geschaffen.


