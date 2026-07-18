from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from infrastructure.portfolio.transaction_record import (
    TransactionRecord,
)


class TransactionCsvRepository:
    """
    Repository lưu và đọc lịch sử giao dịch bằng CSV.

    Format:

    TradeId,Time,Client,Type,Symbol,Quantity,Price,Value

    Responsibility:
    - append TransactionRecord
    - đọc toàn bộ Trade History
    - lọc theo client_id

    Không áp dụng giao dịch vào Portfolio.
    Không tính Average Cost.
    Không sửa client_*.csv.
    """

    FIELDNAMES = [
        "TradeId",
        "Time",
        "Client",
        "Type",
        "Symbol",
        "Quantity",
        "Price",
        "Value",
    ]

    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(
        self,
        csv_path: str,
        encoding: str = "utf-8-sig",
    ):
        if csv_path is None or not str(csv_path).strip():
            raise ValueError("csv_path must not be empty")

        if encoding is None or not str(encoding).strip():
            raise ValueError("encoding must not be empty")

        self._csv_path = Path(str(csv_path).strip())
        self._encoding = str(encoding).strip()

    @property
    def csv_path(self) -> str:
        return str(self._csv_path)

    def append(
        self,
        record: TransactionRecord,
    ) -> None:
        if record is None:
            raise ValueError("record must not be None")

        self._csv_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_exists = self._csv_path.is_file()
        needs_header = (
            not file_exists
            or self._csv_path.stat().st_size == 0
        )

        with self._csv_path.open(
            mode="a",
            encoding=self._encoding,
            newline="",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=self.FIELDNAMES,
            )

            if needs_header:
                writer.writeheader()

            writer.writerow(
                self._record_to_row(record)
            )

    def load_all(self) -> list[TransactionRecord]:
        if not self._csv_path.exists():
            return []

        with self._csv_path.open(
            mode="r",
            encoding=self._encoding,
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            if reader.fieldnames is None:
                return []

            return [
                self._row_to_record(row)
                for row in reader
            ]

    def load_by_client_id(
        self,
        client_id: str,
    ) -> list[TransactionRecord]:
        normalized_client_id = self._normalize_client_id(
            client_id
        )

        return [
            record
            for record in self.load_all()
            if record.client_id == normalized_client_id
        ]

    def contains_trade_id(
        self,
        trade_id: str,
    ) -> bool:
        if trade_id is None or not str(trade_id).strip():
            raise ValueError("trade_id must not be empty")

        normalized_trade_id = str(trade_id).strip()

        return any(
            record.trade_id == normalized_trade_id
            for record in self.load_all()
        )

    def _record_to_row(
        self,
        record: TransactionRecord,
    ) -> dict[str, str]:
        return {
            "TradeId": record.trade_id,
            "Time": record.executed_at.strftime(
                self.DATETIME_FORMAT
            ),
            "Client": record.client_id,
            "Type": record.transaction_type,
            "Symbol": record.symbol,
            "Quantity": self._format_number(
                record.quantity
            ),
            "Price": self._format_number(
                record.price
            ),
            "Value": self._format_number(
                record.gross_value
            ),
        }

    def _row_to_record(
        self,
        row: dict[str, str],
    ) -> TransactionRecord:
        try:
            return TransactionRecord(
                trade_id=str(
                    row.get("TradeId", "")
                ).strip(),
                executed_at=datetime.strptime(
                    str(row.get("Time", "")).strip(),
                    self.DATETIME_FORMAT,
                ),
                client_id=str(
                    row.get("Client", "")
                ).strip(),
                transaction_type=str(
                    row.get("Type", "")
                ).strip(),
                symbol=str(
                    row.get("Symbol", "")
                ).strip(),
                quantity=self._to_float(
                    row.get("Quantity")
                ),
                price=self._to_float(
                    row.get("Price")
                ),
                gross_value=self._to_float(
                    row.get("Value")
                ),
            )

        except Exception as exc:
            raise ValueError(
                f"Invalid transaction history row: {row}"
            ) from exc

    def _normalize_client_id(
        self,
        client_id: str,
    ) -> str:
        if client_id is None or not str(client_id).strip():
            raise ValueError(
                "client_id must not be empty"
            )

        return str(client_id).strip()

    def _to_float(
        self,
        value: object,
    ) -> float:
        if value is None:
            raise ValueError(
                "numeric value must not be empty"
            )

        text = str(value).strip()

        if not text:
            raise ValueError(
                "numeric value must not be empty"
            )

        return float(text.replace(",", ""))

    def _format_number(
        self,
        value: float,
    ) -> str:
        number = float(value)

        if number.is_integer():
            return str(int(number))

        return format(number, ".10f").rstrip("0").rstrip(".")