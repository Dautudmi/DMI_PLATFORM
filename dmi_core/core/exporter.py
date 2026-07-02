"""
=========================================
DMI Framework
Exporter Module
=========================================
"""

from pathlib import Path
import pandas as pd


def save_excel(df, file_path, index=False):
    """
    Lưu DataFrame ra Excel
    """

    file_path = Path(file_path)

    file_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_excel(file_path, index=index)

    return file_path


def save_csv(df, file_path, index=False):
    """
    Lưu DataFrame ra CSV
    """

    file_path = Path(file_path)

    file_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(file_path, index=index, encoding="utf-8-sig")

    return file_path


def save_text(text, file_path):
    """
    Lưu Text Report
    """

    file_path = Path(file_path)

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    return file_path