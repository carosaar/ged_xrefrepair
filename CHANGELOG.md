# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

## [0.5.0] - Detailansicht und genealogische Namensauflösung

### Hinzugefügt

- Interaktive Detailansicht für ausgewählte Analyseergebnisse.
- Einführung des neuen Feldes `related_xref` zur Zuordnung korrespondierender Datensätze.
- Neues Modul `NameResolver` zur Auflösung genealogischer Referenzen.
- Analyseergebnisse enthalten nun zusätzliche Kontextinformationen für die spätere Reparaturvorschau.

### Detailansicht

Für jeden erkannten Problemfall werden nun zusätzliche Informationen angezeigt:

- Problemtyp
- Problemdatensatz
- korrespondierender Datensatz
- ausführliche Problembeschreibung

Die Detailansicht aktualisiert sich automatisch beim Auswählen eines Eintrags in der Problemtabelle.

### Genealogische Namensauflösung

Technische GEDCOM-Referenzen werden nun in sprechende genealogische Informationen aufgelöst.

Personendatensätze (`INDI`) werden dargestellt als:

- Name
- Geburtsdatum (falls vorhanden)
- Sterbedatum (falls vorhanden)

Beispiel:

    Peter Müller (*12 MAR 1887 ✝15 SEP 1951)

Familiendatensätze (`FAM`) werden dargestellt als:

- Ehemann
- Ehefrau
- Heiratsdatum (falls vorhanden)

Beispiel:

    Peter Müller (*1887 ✝1951)
    ⚭ 10 MAY 1910
    Maria Schmidt (*1890 ✝1965)

### Fehlerdarstellung

Nicht auflösbare Referenzen werden nun ausdrücklich gekennzeichnet.

Beispiele:

    @I10@ [Person nicht vorhanden]

    [kein HUSB]

    [kein WIFE]

Dadurch können fehlerhafte Familienverknüpfungen bereits während der Analyse leichter erkannt werden.

### Benutzeroberfläche

- Einführung einer formatierten HTML-Darstellung im Detailbereich.
- Zentrierte Hervorhebung des Problemtyps.
- Verbesserte Lesbarkeit durch getrennte Darstellung von Referenz und Namensauflösung.
- Vorbereitung der Oberfläche für spätere Reparaturvorschau.

### Architektur

- Analyseergebnisse stellen die zugrunde liegenden Datensätze für nachfolgende Verarbeitungsschritte bereit.
- Namensauflösung vollständig von Analyse- und GUI-Logik entkoppelt.
- Grundlage für die spätere Umsetzung von Reparaturaktionen geschaffen.

### Motivation

Mit diesem Meilenstein werden technische GEDCOM-Referenzen erstmals in genealogisch verständliche Informationen übersetzt.

Der Benutzer kann erkannte Probleme nun deutlich leichter nachvollziehen und überprüfen. Gleichzeitig entsteht die Grundlage für eine spätere Reparaturvorschau mit konkreten Änderungsvorschlägen.

---

## [0.4.0] - Problemtabelle und Auswahlmechanismus

### Hinzugefügt

- Gefundene Probleme werden nun in einer Tabelle dargestellt.
- Einführung einer strukturierten Problemliste im Hauptfenster.
- Unterstützung für mehrere tausend Analyseergebnisse in einer übersichtlichen Ansicht.

### Problemtabelle

Die Tabelle enthält jetzt folgende Informationen:

- Problemtyp
- betroffener Datensatz
- Reparierbarkeit
- Problembeschreibung

Jedes erkannte Problem wird als eigene Zeile dargestellt.

### Auswahlmechanismus

- Einführung einer Checkbox-Spalte zur Auswahl einzelner Probleme.
- Standardmäßig werden automatisch reparierbare Probleme vorausgewählt.
- Nicht reparierbare Probleme bleiben standardmäßig deaktiviert.

### Sammelaktionen

Neue Funktionen:

- Alle Probleme auswählen
- Alle Probleme abwählen

Diese Funktionen erleichtern die Arbeit mit großen GEDCOM-Dateien erheblich.

### Statusanzeige

- Anzeige der aktuell ausgewählten Probleme.
- Automatische Aktualisierung beim Setzen oder Entfernen von Häkchen.
- Sofortige Rückmeldung über die Anzahl der zur Reparatur vorgesehenen Einträge.

### Benutzeroberfläche

- Problemliste als zentraler Arbeitsbereich etabliert.
- Analyse- und Dateibereiche optisch überarbeitet.
- Aufteilung des Arbeitsbereichs in Problemliste und zukünftige Detailansicht vorbereitet.

### Motivation

Mit diesem Meilenstein wird die Anwendung erstmals zu einem interaktiven Reparatur-Assistenten.

Der Benutzer kann nun gezielt entscheiden, welche Probleme später korrigiert werden sollen. Die Grundlage für Vorschau, Detailansicht und eigentliche Reparaturfunktionen ist damit geschaffen.



---
## [0.3.0] - Anzeige gefundener Referenzprobleme

### Hinzugefügt

- Analyseergebnisse enthalten nun die vollständige Liste erkannter Probleme.
- Gefundene Referenzfehler werden dem Benutzer angezeigt.
- Einführung einer strukturierten Übergabe von Issue-Objekten zwischen Analyse- und GUI-Schicht.

### Benutzeroberfläche

- Die Analyse zeigt nicht mehr nur die Anzahl der Probleme.
- Zu jedem Problem wird nun eine Beschreibung angezeigt.
- Der Benutzer kann nachvollziehen, warum ein Datensatz als inkonsistent erkannt wurde.

### Motivation

Bevor automatische Reparaturen angeboten werden können, muss die Analyse für den Benutzer nachvollziehbar und überprüfbar sein. 
Dieser Meilenstein schafft die Grundlage für die spätere Einführung einer Reparaturvorschau und selektiver Korrekturen.

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


