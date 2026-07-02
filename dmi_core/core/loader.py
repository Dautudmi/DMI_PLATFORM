import pandas as pd
from pathlib import Path


def load_csv(file_path, encoding="utf-8"):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File không tồn tại: {file_path}")

    try:
        df = pd.read_csv(file_path, encoding=encoding)
        return df

    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8-sig")
        return df


def load_excel(file_path, sheet_name=0):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File không tồn tại: {file_path}")

    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df


def save_csv(df, file_path, index=False, encoding="utf-8-sig"):
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(file_path, index=index, encoding=encoding)


def save_excel(df, file_path, index=False):
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_excel(file_path, index=index)