# Untechnische Projektbeschreibung
## GED XRef Repair

GED XRef Repair ist ein Werkzeug zur Qualitätsprüfung und Reparatur von GEDCOM-Dateien.

Beim Austausch genealogischer Daten zwischen verschiedenen Programmen entstehen gelegentlich fehlerhafte oder unvollständige Verknüpfungen zwischen Personen- und Familiendatensätzen. Solche Fehler können dazu führen, dass Familienbeziehungen unvollständig dargestellt werden oder Personen scheinbar ihre Eltern, Kinder oder Partner verlieren.

GED XRef Repair analysiert GEDCOM-Dateien auf solche Inkonsistenzen und erstellt daraus einen nachvollziehbaren Reparaturvorschlag.

### Wesentliche Ziele:

* Keine automatische Änderung ohne Zustimmung des Benutzers.
* Jede vorgeschlagene Änderung wird eindeutig erklärt.
* Vor jeder Reparatur wird die geplante Änderung in einer Vorschau angezeigt.
* Mehrdeutige oder fachlich nicht sicher lösbare Fehler werden ausschließlich gemeldet und nicht automatisch korrigiert.
* Die Originaldatei bleibt unverändert.
* Reparierte Daten werden grundsätzlich in einer neuen GEDCOM-Datei gespeichert.

Das Werkzeug richtet sich an Familienforscher, Genealogen und Betreiber von genealogischen Datenbanken, die die strukturelle Konsistenz ihrer GEDCOM-Dateien sicherstellen möchten.