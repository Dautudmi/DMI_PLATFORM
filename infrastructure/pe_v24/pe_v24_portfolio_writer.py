from __future__ import annotations

import csv
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from apps.portfolio.models.portfolio import Portfolio
from infrastructure.pe_v24.pe_v24_portfolio_write_result import (
    PEV24PortfolioWriteResult,
)


class PEV24PortfolioWriter:
    """
    Ghi Portfolio Domain về file client_<client_id>.csv của PE_V2.4.

    Format chuẩn:

    Ticker,Quantity,AverageCost

    Responsibility:
    - xác định file theo client_id
    - tạo backup file cũ
    - ghi file tạm
    - thay thế file thật theo cơ chế atomic replace
    - trả về kết quả ghi

    Không tính Quantity.
    Không tính Average Cost.
    Không áp dụng Transaction.
    Không ghi Trade History.
    """

    FIELDNAMES = [
        "Ticker",
        "Quantity",
        "AverageCost",
    ]

    def __init__(
        self,
        clients_folder_path: str,
        file_prefix: str = "client_",
        file_suffix: str = ".csv",
        encoding: str = "utf-8-sig",
        backup_folder_name: str = "_portfolio_backups",
        clock: Any | None = None,
    ):
        if clients_folder_path is None or not str(
            clients_folder_path
        ).strip():
            raise ValueError(
                "clients_folder_path must not be empty"
            )

        if file_prefix is None:
            raise ValueError("file_prefix must not be None")

        if file_suffix is None or not str(file_suffix).strip():
            raise ValueError("file_suffix must not be empty")

        if encoding is None or not str(encoding).strip():
            raise ValueError("encoding must not be empty")

        if backup_folder_name is None or not str(
            backup_folder_name
        ).strip():
            raise ValueError(
                "backup_folder_name must not be empty"
            )

        self._clients_folder_path = Path(
            str(clients_folder_path).strip()
        )
        self._file_prefix = str(file_prefix)
        self._file_suffix = str(file_suffix).strip()
        self._encoding = str(encoding).strip()
        self._backup_folder_name = str(
            backup_folder_name
        ).strip()
        self._clock = clock

    @property
    def clients_folder_path(self) -> str:
        return str(self._clients_folder_path)

    def get_portfolio_path(self, client_id: str) -> str:
        normalized_client_id = self._normalize_client_id(
            client_id
        )

        file_name = (
            f"{self._file_prefix}"
            f"{normalized_client_id}"
            f"{self._file_suffix}"
        )

        return str(self._clients_folder_path / file_name)

    def write(
        self,
        portfolio: Portfolio,
    ) -> PEV24PortfolioWriteResult:
        if portfolio is None:
            raise ValueError("portfolio must not be None")

        client_id = self._normalize_client_id(
            portfolio.client_name
        )

        file_path = Path(
            self.get_portfolio_path(client_id)
        )

        temporary_path = file_path.with_suffix(
            file_path.suffix + ".tmp"
        )

        backup_path: Path | None = None

        try:
            self._validate_portfolio(portfolio)

            file_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            if file_path.exists():
                backup_path = self._create_backup(
                    source_path=file_path,
                    client_id=client_id,
                )

            self._write_temporary_file(
                temporary_path=temporary_path,
                portfolio=portfolio,
            )

            temporary_path.replace(file_path)

            return PEV24PortfolioWriteResult(
                success=True,
                client_id=client_id,
                file_path=str(file_path),
                total_positions=len(portfolio.holdings),
                backup_path=(
                    str(backup_path)
                    if backup_path is not None
                    else None
                ),
                error=None,
            )

        except Exception as exc:
            if temporary_path.exists():
                temporary_path.unlink()

            return PEV24PortfolioWriteResult(
                success=False,
                client_id=client_id,
                file_path=str(file_path),
                total_positions=0,
                backup_path=(
                    str(backup_path)
                    if backup_path is not None
                    else None
                ),
                error=str(exc),
            )

    def _write_temporary_file(
        self,
        temporary_path: Path,
        portfolio: Portfolio,
    ) -> None:
        with temporary_path.open(
            mode="w",
            encoding=self._encoding,
            newline="",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=self.FIELDNAMES,
            )

            writer.writeheader()

            for holding in sorted(
                portfolio.holdings,
                key=lambda item: str(
                    item.symbol
                ).strip().upper(),
            ):
                writer.writerow(
                    {
                        "Ticker": str(
                            holding.symbol
                        ).strip().upper(),
                        "Quantity": self._format_number(
                            holding.quantity
                        ),
                        "AverageCost": self._format_number(
                            holding.average_cost
                        ),
                    }
                )

    def _create_backup(
        self,
        source_path: Path,
        client_id: str,
    ) -> Path:
        timestamp = self._now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        backup_folder = (
            self._clients_folder_path
            / self._backup_folder_name
            / client_id
        )

        backup_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        backup_path = backup_folder / (
            f"{source_path.stem}_{timestamp}"
            f"{source_path.suffix}"
        )

        shutil.copy2(
            source_path,
            backup_path,
        )

        return backup_path

    def _validate_portfolio(
        self,
        portfolio: Portfolio,
    ) -> None:
        seen_symbols: set[str] = set()

        for holding in portfolio.holdings:
            symbol = str(
                holding.symbol
            ).strip().upper()

            if not symbol:
                raise ValueError(
                    "holding symbol must not be empty"
                )

            if symbol in seen_symbols:
                raise ValueError(
                    f"duplicate holding symbol: {symbol}"
                )

            if float(holding.quantity) <= 0:
                raise ValueError(
                    f"holding quantity must be greater "
                    f"than 0 for symbol {symbol}"
                )

            if float(holding.average_cost) < 0:
                raise ValueError(
                    f"holding average_cost must not be "
                    f"negative for symbol {symbol}"
                )

            seen_symbols.add(symbol)

    def _normalize_client_id(
        self,
        client_id: str,
    ) -> str:
        if client_id is None or not str(client_id).strip():
            raise ValueError(
                "client_id must not be empty"
            )

        normalized = str(client_id).strip()

        if "/" in normalized or "\\" in normalized:
            raise ValueError(
                "client_id contains invalid path characters"
            )

        if normalized in {".", ".."}:
            raise ValueError(
                "client_id contains invalid path characters"
            )

        return normalized

    def _format_number(
        self,
        value: float,
    ) -> str:
        number = float(value)

        if number.is_integer():
            return str(int(number))

        return format(
            number,
            ".10f",
        ).rstrip("0").rstrip(".")

    def _now(self) -> datetime:
        if self._clock is None:
            return datetime.now()

        if not hasattr(self._clock, "now"):
            raise AttributeError(
                "clock must have now method"
            )

        value = self._clock.now()

        if not isinstance(value, datetime):
            raise TypeError(
                "clock.now must return datetime"
            )

        return value