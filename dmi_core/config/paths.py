"""
==================================================
DMI Investment Platform
Core Configuration
File: paths.py
Version: 1.0
==================================================
"""

from pathlib import Path


# ==================================================
# ROOT PATH
# ==================================================

ROOT = Path("F:/")

PYTHON_DIR = ROOT / "Python"

DATA_DIR = ROOT / "DATA"

BACKUP_DIR = ROOT / "BACKUP_DMI"


# ==================================================
# DATA
# ==================================================

CAFEF_DIR = DATA_DIR / "CafeF"

FUNDAMENTAL_DIR = DATA_DIR / "Fundamental"

VALUATION_DIR = DATA_DIR / "Valuation"

PORTFOLIO_DIR = DATA_DIR / "Portfolio"

MACRO_DIR = DATA_DIR / "Macro"

REPORT_DIR = DATA_DIR / "Reports"


# ==================================================
# MAIN FILES
# ==================================================

CAFEF_ALL = CAFEF_DIR / "CafeF_ALL.csv"

FUNDAMENTAL_ALL = FUNDAMENTAL_DIR / "Fundamental_ALL.csv"

VALUATION_TARGET = VALUATION_DIR / "valuation_target.csv"


# ==================================================
# PROJECTS
# ==================================================

PE_PROJECT = PYTHON_DIR / "PE_V2.4"

MME_PROJECT = PYTHON_DIR / "MME_V1.0"

MACRO_PROJECT = PYTHON_DIR / "MACRO_ENGINE_V1.0"

VALUATION_PROJECT = PYTHON_DIR / "VALUATION_ENGINE_V1.0"

FUNDAMENTAL_PROJECT = PYTHON_DIR / "FUNDAMENTAL_ENGINE_V1.0"

CORE_PROJECT = PYTHON_DIR / "DMI_CORE_V1.0"