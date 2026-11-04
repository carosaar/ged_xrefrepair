from pathlib import Path

PROJECT_FILES = {
    "src/ged_xrefrepair/__init__.py":
        '__version__ = "0.1.0"\n',

    "src/ged_xrefrepair/__main__.py":
        """from ged_xrefrepair.main import main

if __name__ == "__main__":
    main()
""",

    "src/ged_xrefrepair/main.py":
        """from PySide6.QtWidgets import QApplication
from ged_xrefrepair.gui.main_window import MainWindow

import sys


def main() -> None:
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
""",

    "src/ged_xrefrepair/gui/main_window.py":
        """from PySide6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("GED XRef Repair")
        self.resize(1200, 800)
""",

    "src/ged_xrefrepair/model/issue.py":
        """from dataclasses import dataclass


@dataclass(slots=True)
class Issue:
    issue_type: str
    severity: str
    description: str
    auto_repair_possible: bool
""",

    "src/ged_xrefrepair/model/repair_action.py":
        """from dataclasses import dataclass


@dataclass(slots=True)
class RepairAction:
    title: str
    record_id: str
    old_text: str
    new_text: str
    selected: bool = True
""",

    "src/ged_xrefrepair/parser/gedcom_parser.py":
        """class GedcomParser:
    pass
""",

    "src/ged_xrefrepair/parser/gedcom_writer.py":
        """class GedcomWriter:
    pass
""",

    "src/ged_xrefrepair/analyzer/reference_analyzer.py":
        """class ReferenceAnalyzer:
    pass
""",

    "src/ged_xrefrepair/repair/repair_engine.py":
        """class RepairEngine:
    pass
""",

    "src/ged_xrefrepair/services/analysis_service.py":
        """class AnalysisService:
    pass
""",

    "src/ged_xrefrepair/services/repair_service.py":
        """class RepairService:
    pass
"""
}

EMPTY_FILES = [
    "src/ged_xrefrepair/gui/__init__.py",
    "src/ged_xrefrepair/gui/analysis_dialog.py",
    "src/ged_xrefrepair/gui/repair_dialog.py",
    "src/ged_xrefrepair/gui/diff_dialog.py",
    "src/ged_xrefrepair/gui/about_dialog.py",

    "src/ged_xrefrepair/model/__init__.py",
    "src/ged_xrefrepair/model/gedcom_record.py",
    "src/ged_xrefrepair/model/individual.py",
    "src/ged_xrefrepair/model/family.py",

    "src/ged_xrefrepair/parser/__init__.py",

    "src/ged_xrefrepair/analyzer/__init__.py",
    "src/ged_xrefrepair/analyzer/family_consistency.py",
    "src/ged_xrefrepair/analyzer/analysis_result.py",

    "src/ged_xrefrepair/repair/__init__.py",
    "src/ged_xrefrepair/repair/chil_repairs.py",
    "src/ged_xrefrepair/repair/famc_repairs.py",
    "src/ged_xrefrepair/repair/fams_repairs.py",
    "src/ged_xrefrepair/repair/orphan_reference_repairs.py",

    "src/ged_xrefrepair/services/__init__.py",
    "src/ged_xrefrepair/services/export_service.py",
    "src/ged_xrefrepair/services/report_service.py",

    "src/ged_xrefrepair/reports/__init__.py",
    "src/ged_xrefrepair/reports/html_report.py",
    "src/ged_xrefrepair/reports/txt_report.py",

    "tests/parser/test_parser.py",
    "tests/analyzer/test_reference_analysis.py",
    "tests/repair/test_chil_repairs.py",
    "tests/repair/test_famc_repairs.py",
    "tests/repair/test_fams_repairs.py",
]

DIRECTORIES = [
    "src/ged_xrefrepair/gui",
    "src/ged_xrefrepair/model",
    "src/ged_xrefrepair/parser",
    "src/ged_xrefrepair/analyzer",
    "src/ged_xrefrepair/repair",
    "src/ged_xrefrepair/services",
    "src/ged_xrefrepair/reports",
    "src/ged_xrefrepair/resources/icons",
    "src/ged_xrefrepair/resources/translations",

    "tests/parser",
    "tests/analyzer",
    "tests/repair",
    "tests/services",
    "tests/sample_data",

    "docs/screenshots",
    "examples/expected_results",
]


PYPROJECT = """
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "ged-xrefrepair"
version = "0.1.0"
description = "GEDCOM Cross Reference Repair Assistant"
readme = "README.md"
requires-python = ">=3.12"

authors = [
    {name = "Dieter Eckstein"}
]

dependencies = [
    "PySide6>=6.8"
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0"
]

[project.scripts]
ged-xrefrepair = "ged_xrefrepair.main:main"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-v"
"""


GITIGNORE = """
__pycache__/
*.pyc
*.pyo
*.pyd

.venv/
venv/
env/

build/
dist/
*.egg-info/

.pytest_cache/
.coverage
htmlcov/

.vscode/
.idea/

Thumbs.db
desktop.ini
.DS_Store

*.log
*.tmp
*.bak
*.old

output/
reports/

*.ged
*.gedcom
"""


README = """
# GED XRef Repair

Werkzeug zur Analyse und Reparatur von GEDCOM-Referenzen.

Aktuelle Ziele:

- FAMC ↔ CHIL Konsistenz
- FAMS ↔ HUSB/WIFE Konsistenz
- Erkennung verwaister Referenzen
- Reparaturvorschläge mit Benutzerbestätigung
- Qt Desktop GUI
"""


def create_file(path_str: str, content: str = "") -> None:
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.write_text(content, encoding="utf-8")
        print(f"[CREATE] {path}")
    else:
        print(f"[SKIP]   {path}")


def main() -> None:

    for directory in DIRECTORIES:
        Path(directory).mkdir(parents=True, exist_ok=True)

    for file_name, content in PROJECT_FILES.items():
        create_file(file_name, content)

    for file_name in EMPTY_FILES:
        create_file(file_name)

    create_file("README.md", README)
    create_file(".gitignore", GITIGNORE)
    create_file("pyproject.toml", PYPROJECT)
    create_file("requirements.txt", "PySide6\npytest\npytest-cov\n")

    print()
    print("Projektstruktur erstellt.")


if __name__ == "__main__":
    main()