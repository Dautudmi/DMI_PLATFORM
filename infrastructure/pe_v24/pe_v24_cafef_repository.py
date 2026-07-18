from infrastructure.csv_repository import CsvRepository
from infrastructure.pe_v24.pe_v24_paths import PEV24Paths
from infrastructure.pe_v24.pe_v24_stock_row import PEV24StockRow


class PEV24CafeFRepository:
    """
    Adapter đọc CafeF_ALL.csv từ PE_V2.4.

    Responsibility:
    - đọc dữ liệu CSV PE_V2.4
    - map row thô thành PEV24StockRow
    - chưa chuyển sang domain DMI chính thức

    Không tính BUY.
    Không tính Health.
    Không render.
    Không gửi Telegram.
    """

    def __init__(
        self,
        paths: PEV24Paths,
        csv_repository: CsvRepository | None = None,
    ):
        if paths is None:
            raise ValueError("paths must not be None")

        self._paths = paths
        self._csv_repository = csv_repository or CsvRepository()

    def load_rows(self) -> list[PEV24StockRow]:
        path = self._paths.require_cafef_all_csv_path()
        rows = self._csv_repository.read_rows(path)

        return [self._map_row(row) for row in rows]

    def load_symbols(self) -> list[str]:
        rows = self.load_rows()

        symbols: list[str] = []

        for row in rows:
            if row.symbol and row.symbol not in symbols:
                symbols.append(row.symbol)

        return symbols

    def load_latest_by_symbol(self) -> dict[str, PEV24StockRow]:
        rows = self.load_rows()

        latest: dict[str, PEV24StockRow] = {}

        for row in rows:
            if not row.symbol:
                continue

            latest[row.symbol] = row

        return latest

    def _map_row(self, row: dict) -> PEV24StockRow:
        symbol = self._get_first(row, ["symbol", "Symbol", "ticker", "Ticker", "code", "Code"])

        return PEV24StockRow(
            symbol=str(symbol).strip().upper() if symbol is not None else "",
            date=self._get_first(row, ["date", "Date", "trading_date", "TradingDate", "time", "Time"]),
            close=self._to_float(
                self._get_first(row, ["close", "Close", "price", "Price", "adj_close", "Adj Close"])
            ),
            volume=self._to_float(
                self._get_first(row, ["volume", "Volume", "vol", "Vol"])
            ),
            raw=row,
        )

    def _get_first(self, row: dict, keys: list[str]):
        for key in keys:
            if key in row:
                return row[key]

        return None

    def _to_float(self, value):
        if value is None:
            return None

        text = str(value).strip()

        if not text:
            return None

        try:
            return float(text.replace(",", ""))
        except ValueError:
            return None