@echo off
echo Erzeuge Projektstruktur fuer ged_xrefrepair ...
echo.

REM Hauptverzeichnisse
mkdir src
mkdir tests
mkdir docs
mkdir examples
mkdir build
mkdir dist

REM Python-Quellcode
mkdir src\ged_xrefrepair

REM GUI
mkdir src\ged_xrefrepair\gui

REM Datenmodelle
mkdir src\ged_xrefrepair\model

REM Parser
mkdir src\ged_xrefrepair\parser

REM Analyse
mkdir src\ged_xrefrepair\analyzer

REM Reparatur
mkdir src\ged_xrefrepair\repair

REM Berichte
mkdir src\ged_xrefrepair\reports

REM Ressourcen
mkdir src\ged_xrefrepair\resources
mkdir src\ged_xrefrepair\resources\icons
mkdir src\ged_xrefrepair\resources\translations

REM Tests
mkdir tests\parser
mkdir tests\analyzer
mkdir tests\repair
mkdir tests\sample_data

REM Dokumentation
mkdir docs\screenshots

REM Beispiele
mkdir examples\expected_results

REM Python-Pakete
type nul > src\ged_xrefrepair\__init__.py
type nul > src\ged_xrefrepair\gui\__init__.py
type nul > src\ged_xrefrepair\model\__init__.py
type nul > src\ged_xrefrepair\parser\__init__.py
type nul > src\ged_xrefrepair\analyzer\__init__.py
type nul > src\ged_xrefrepair\repair\__init__.py
type nul > src\ged_xrefrepair\reports\__init__.py

REM Einstiegspunkt
type nul > src\ged_xrefrepair\main.py

REM GUI-Dateien
type nul > src\ged_xrefrepair\gui\main_window.py
type nul > src\ged_xrefrepair\gui\analysis_dialog.py
type nul > src\ged_xrefrepair\gui\repair_dialog.py
type nul > src\ged_xrefrepair\gui\diff_dialog.py
type nul > src\ged_xrefrepair\gui\about_dialog.py

REM Modelle
type nul > src\ged_xrefrepair\model\gedcom_record.py
type nul > src\ged_xrefrepair\model\individual.py
type nul > src\ged_xrefrepair\model\family.py
type nul > src\ged_xrefrepair\model\issue.py
type nul > src\ged_xrefrepair\model\repair_action.py

REM Parser
type nul > src\ged_xrefrepair\parser\gedcom_parser.py
type nul > src\ged_xrefrepair\parser\gedcom_writer.py

REM Analyse
type nul > src\ged_xrefrepair\analyzer\reference_analyzer.py
type nul > src\ged_xrefrepair\analyzer\family_consistency.py
type nul > src\ged_xrefrepair\analyzer\validation_result.py

REM Reparatur
type nul > src\ged_xrefrepair\repair\repair_engine.py
type nul > src\ged_xrefrepair\repair\chil_repairs.py
type nul > src\ged_xrefrepair\repair\famc_repairs.py
type nul > src\ged_xrefrepair\repair\fams_repairs.py
type nul > src\ged_xrefrepair\repair\orphan_reference_repairs.py

REM Berichte
type nul > src\ged_xrefrepair\reports\html_report.py
type nul > src\ged_xrefrepair\reports\txt_report.py

REM Projektdokumente
type nul > README.md
type nul > LICENSE
type nul > requirements.txt
type nul > pyproject.toml
type nul > .gitignore

echo.
echo Projektstruktur erfolgreich erzeugt.
pause