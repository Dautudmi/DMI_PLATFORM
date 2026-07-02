"""
DMI Framework
Global Settings
Version: 1.0
"""

# =========================
# SYSTEM
# =========================

PROJECT_NAME = "DMI Framework"
VERSION = "1.0"
AUTHOR = "Đức Mạnh"

ENV = "DEV"   # DEV / PROD
DEBUG = True

TIMEZONE = "Asia/Ho_Chi_Minh"

# =========================
# DATA
# =========================

DEFAULT_ENCODING = "utf-8-sig"
CSV_SEPARATOR = ","

# =========================
# REPORT
# =========================

EXPORT_EXCEL = True
EXPORT_CSV = True
EXPORT_TEXT = True

# =========================
# LOGGING
# =========================

LOG_TO_FILE = True
LOG_TO_CONSOLE = True

# =========================
# ENGINE FLAGS
# =========================

ENABLE_TELEGRAM = False
ENABLE_SCHEDULER = False