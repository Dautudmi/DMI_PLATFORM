from pathlib import Path

from infrastructure.csv_repository import CsvRepository
from infrastructure.pe_v24.pe_v24_client_position import (
    PEV24ClientPosition,
)
from infrastructure.pe_v24.pe_v24_mapper import PEV24Mapper


class PEV24ClientPortfolioRepository:
    """
    Repository đọc danh mục riêng của từng khách hàng PE_V2.4.

    Quy ước file:

    client_<client_id>.csv

    Ví dụ:

    client_anh_manh.csv

    Format chuẩn:

    Ticker,Quantity,Cost
    NAB,1000,12.300
    FTS,500,26.465

    Responsibility:
    - xác định đường dẫn file từ client_id
    - đọc CSV danh mục khách
    - map dữ liệu thành PEV24ClientPosition
    - kiểm tra dữ liệu Quantity và Cost

    Không tạo Portfolio Domain.
    Không tính Recommendation.
    Không tính Decision.
    """

    def __init__(
        self,
        clients_folder_path: str,
        csv_repository: CsvRepository | None = None,
        file_prefix: str = "client_",
        file_suffix: str = ".csv",
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

        self._clients_folder_path = Path(
            str(clients_folder_path).strip()
        )
        self._csv_repository = (
            csv_repository or CsvRepository()
        )
        self._file_prefix = str(file_prefix)
        self._file_suffix = str(file_suffix)
        self._mapper = PEV24Mapper()

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

    def exists(self, client_id: str) -> bool:
        return Path(
            self.get_portfolio_path(client_id)
        ).is_file()

    def load_portfolio(
        self,
        client_id: str,
    ) -> list[PEV24ClientPosition]:
        path = self.get_portfolio_path(client_id)
        rows = self._csv_repository.read_rows(path)

        positions: list[PEV24ClientPosition] = []

        for row_number, row in enumerate(rows, start=2):
            position = self._map_row(
                row=row,
                row_number=row_number,
            )

            if position.ticker:
                positions.append(position)

        return positions

    def load_symbols(self, client_id: str) -> list[str]:
        symbols: list[str] = []

        for position in self.load_portfolio(client_id):
            if position.ticker not in symbols:
                symbols.append(position.ticker)

        return symbols

    def _map_row(
        self,
        row: dict,
        row_number: int,
    ) -> PEV24ClientPosition:
        ticker_value = self._mapper.get_first(
            row,
            [
                "Ticker",
                "ticker",
                "Symbol",
                "symbol",
                "Code",
                "code",
            ],
        )

        quantity_value = self._mapper.get_first(
            row,
            [
                "Quantity",
                "quantity",
                "Qty",
                "qty",
                "Volume",
                "volume",
            ],
        )

        cost_value = self._mapper.get_first(
            row,
            [
                "Cost",
                "cost",
                "CostPrice",
                "cost_price",
                "AverageCost",
                "average_cost",
                "AvgPrice",
                "avg_price",
            ],
        )

        ticker = self._mapper.to_symbol(ticker_value)
        quantity = self._mapper.to_float(quantity_value)
        cost = self._mapper.to_float(cost_value)

        if not ticker:
            return PEV24ClientPosition(
                ticker="",
                quantity=0.0,
                cost=0.0,
                raw=row,
            )

        if quantity is None:
            raise ValueError(
                f"Missing Quantity for ticker {ticker} "
                f"at row {row_number}"
            )

        if quantity <= 0:
            raise ValueError(
                f"Quantity must be greater than 0 "
                f"for ticker {ticker} at row {row_number}"
            )

        if cost is None:
            raise ValueError(
                f"Missing Cost for ticker {ticker} "
                f"at row {row_number}"
            )

        if cost < 0:
            raise ValueError(
                f"Cost must not be negative "
                f"for ticker {ticker} at row {row_number}"
            )

        return PEV24ClientPosition(
            ticker=ticker,
            quantity=quantity,
            cost=cost,
            raw=row,
        )

    def _normalize_client_id(self, client_id: str) -> str:
        if client_id is None or not str(client_id).strip():
            raise ValueError("client_id must not be empty")

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