from infrastructure.csv_repository import CsvRepository
from infrastructure.pe_v24.pe_v24_holding import PEV24Holding
from infrastructure.pe_v24.pe_v24_mapper import PEV24Mapper


class PEV24PortfolioRepository:
    def __init__(self, csv_path: str, csv_repository: CsvRepository | None = None):
        if csv_path is None or not str(csv_path).strip():
            raise ValueError("csv_path must not be empty")

        self._csv_path = str(csv_path).strip()
        self._csv_repository = csv_repository or CsvRepository()
        self._mapper = PEV24Mapper()

    def load_holdings(self) -> list[PEV24Holding]:
        rows = self._csv_repository.read_rows(self._csv_path)
        return [self._map_row(row) for row in rows]

    def load_by_client_id(self, client_id: str) -> list[PEV24Holding]:
        if client_id is None or not str(client_id).strip():
            raise ValueError("client_id must not be empty")

        normalized = str(client_id).strip()

        return [
            holding
            for holding in self.load_holdings()
            if holding.client_id == normalized
        ]

    def _map_row(self, row: dict) -> PEV24Holding:
        client_id = self._mapper.get_first(
            row,
            ["client_id", "ClientID", "id", "ID"],
        )

        symbol = self._mapper.get_first(
            row,
            ["symbol", "Symbol", "ticker", "Ticker", "code", "Code"],
        )

        quantity = self._mapper.get_first(
            row,
            ["quantity", "Quantity", "qty", "Qty", "volume", "Volume"],
        )

        cost_price = self._mapper.get_first(
            row,
            ["cost_price", "CostPrice", "cost", "Cost", "avg_price", "AvgPrice"],
        )

        return PEV24Holding(
            client_id=str(client_id).strip() if client_id is not None else "",
            symbol=self._mapper.to_symbol(symbol),
            quantity=self._mapper.to_float(quantity),
            cost_price=self._mapper.to_float(cost_price),
            raw=row,
        )