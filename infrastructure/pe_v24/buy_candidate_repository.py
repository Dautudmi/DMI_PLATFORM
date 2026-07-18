from infrastructure.csv_repository import CsvRepository
from infrastructure.pe_v24.pe_v24_buy_candidate import PEV24BuyCandidate
from infrastructure.pe_v24.pe_v24_mapper import PEV24Mapper


class PEV24BuyCandidateRepository:
    def __init__(self, csv_path: str, csv_repository: CsvRepository | None = None):
        if csv_path is None or not str(csv_path).strip():
            raise ValueError("csv_path must not be empty")

        self._csv_path = str(csv_path).strip()
        self._csv_repository = csv_repository or CsvRepository()
        self._mapper = PEV24Mapper()

    def load_candidates(self) -> list[PEV24BuyCandidate]:
        rows = self._csv_repository.read_rows(self._csv_path)
        return [self._map_row(row) for row in rows]

    def load_symbols(self) -> list[str]:
        symbols: list[str] = []

        for candidate in self.load_candidates():
            if candidate.symbol and candidate.symbol not in symbols:
                symbols.append(candidate.symbol)

        return symbols

    def _map_row(self, row: dict) -> PEV24BuyCandidate:
        symbol = self._mapper.get_first(
            row,
            ["symbol", "Symbol", "ticker", "Ticker", "code", "Code"],
        )

        strategy = self._mapper.get_first(
            row,
            ["strategy", "Strategy", "signal", "Signal"],
        )

        score = self._mapper.get_first(
            row,
            ["score", "Score", "rank_score", "RankScore"],
        )

        return PEV24BuyCandidate(
            symbol=self._mapper.to_symbol(symbol),
            strategy=self._mapper.to_text(strategy),
            score=self._mapper.to_float(score),
            raw=row,
        )