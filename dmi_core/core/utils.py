"""
==================================================
DMI Framework
Core Utilities
Version : 1.0
==================================================
"""

from datetime import datetime
from pathlib import Path
import os


# ======================================================
# TIME
# ======================================================

def now():
    """Trả về thời gian hiện tại"""
    return datetime.now()


def today():
    """YYYY-MM-DD"""
    return datetime.now().strftime("%Y-%m-%d")


def timestamp():
    """YYYYMMDD_HHMMSS"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# ======================================================
# FOLDER
# ======================================================

def ensure_folder(folder):

    folder = Path(folder)

    folder.mkdir(parents=True, exist_ok=True)

    return folder


# ======================================================
# FILE
# ======================================================

def file_exists(file):

    return Path(file).exists()


def file_size_mb(file):

    size = os.path.getsize(file)

    return round(size / 1024 / 1024, 2)


# ======================================================
# STRING
# ======================================================

def line(length=60):

    return "=" * length


def title(text):

    print()

    print(line())

    print(text)

    print(line())