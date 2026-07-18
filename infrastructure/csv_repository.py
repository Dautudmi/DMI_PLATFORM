import csv
from pathlib import Path


class CsvRepository:
    """
    Generic CSV repository.
    """

    def read_rows(self, path: str, encoding: str = "utf-8-sig") -> list[dict[str, str]]:
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")

        with file_path.open("r", encoding=encoding, newline="") as file:
            reader = csv.DictReader(file)
            return [dict(row) for row in reader]

    def write_rows(
        self,
        path: str,
        rows: list[dict],
        encoding: str = "utf-8-sig",
    ) -> None:
        if rows is None:
            raise ValueError("rows must not be None")

        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = self._collect_fieldnames(rows)

        with file_path.open("w", encoding=encoding, newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def _collect_fieldnames(self, rows: list[dict]) -> list[str]:
        fieldnames: list[str] = []

        for row in rows:
            for key in row.keys():
                if key not in fieldnames:
                    fieldnames.append(key)

        return fieldnames