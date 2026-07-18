from typing import Any

from apps.stock.application.stock_application_result import StockApplicationResult


class StockApplication:
    """
    Stock Application Foundation.

    Responsibility:
    - nhận stock repository
    - đọc rows/symbols
    - trả về kết quả tổng quan

    Không tính BUY.
    Không tính Health.
    Không tính Decision.
    Không render.
    Không gửi Telegram.
    """

    def __init__(self, stock_repository: Any):
        if stock_repository is None:
            raise ValueError("stock_repository must not be None")

        self._stock_repository = stock_repository

    def inspect(self) -> StockApplicationResult:
        try:
            rows = self._load_rows()
            symbols = self._load_symbols(rows)

            return StockApplicationResult(
                success=True,
                total_rows=len(rows),
                total_symbols=len(symbols),
                data={
                    "rows": rows,
                    "symbols": symbols,
                },
                error=None,
            )

        except Exception as exc:
            return StockApplicationResult(
                success=False,
                total_rows=0,
                total_symbols=0,
                data=None,
                error=str(exc),
            )

    def _load_rows(self) -> list[Any]:
        if hasattr(self._stock_repository, "load_rows"):
            return self._stock_repository.load_rows()

        raise AttributeError("stock_repository must have load_rows method")

    def _load_symbols(self, rows: list[Any]) -> list[str]:
        if hasattr(self._stock_repository, "load_symbols"):
            return self._stock_repository.load_symbols()

        symbols: list[str] = []

        for row in rows:
            symbol = self._extract_symbol(row)

            if symbol and symbol not in symbols:
                symbols.append(symbol)

        return symbols

    def _extract_symbol(self, row: Any) -> str:
        if hasattr(row, "symbol"):
            return str(row.symbol).strip().upper()

        if isinstance(row, dict):
            for key in ["symbol", "Symbol", "ticker", "Ticker", "code", "Code"]:
                if key in row:
                    return str(row[key]).strip().upper()

        return ""