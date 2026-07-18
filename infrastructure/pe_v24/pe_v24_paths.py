from dataclasses import dataclass


@dataclass(frozen=True)
class PEV24Paths:
    cafef_all_csv_path: str
    buy_candidates_path: str | None = None
    clients_folder_path: str | None = None
    reports_folder_path: str | None = None

    def require_cafef_all_csv_path(self) -> str:
        if not self.cafef_all_csv_path or not str(self.cafef_all_csv_path).strip():
            raise ValueError("cafef_all_csv_path must not be empty")

        return str(self.cafef_all_csv_path).strip()