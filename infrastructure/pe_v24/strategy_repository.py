from infrastructure.csv_repository import CsvRepository
from infrastructure.pe_v24.pe_v24_strategy import PEV24Strategy
from infrastructure.pe_v24.pe_v24_mapper import PEV24Mapper


class PEV24StrategyRepository:
    def __init__(self, csv_path: str, csv_repository: CsvRepository | None = None):
        if csv_path is None or not str(csv_path).strip():
            raise ValueError("csv_path must not be empty")

        self._csv_path = str(csv_path).strip()
        self._csv_repository = csv_repository or CsvRepository()
        self._mapper = PEV24Mapper()

    def load_strategies(self) -> list[PEV24Strategy]:
        rows = self._csv_repository.read_rows(self._csv_path)
        return [self._map_row(row) for row in rows]

    def load_strategy_by_symbol(self) -> dict[str, str]:
        result: dict[str, str] = {}

        for item in self.load_strategies():
            if item.symbol and item.strategy:
                result[item.symbol] = item.strategy

        return result

    def _map_row(self, row: dict) -> PEV24Strategy:
        symbol = self._mapper.get_first(
            row,
            ["symbol", "Symbol", "ticker", "Ticker", "code", "Code"],
        )

        strategy = self._mapper.get_first(
            row,
            ["strategy", "Strategy", "signal", "Signal"],
        )

        return PEV24Strategy(
            symbol=self._mapper.to_symbol(symbol),
            strategy=self._mapper.to_text(strategy) or "",
            raw=row,
        )