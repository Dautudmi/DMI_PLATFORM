from infrastructure.csv_repository import CsvRepository
from infrastructure.pe_v24.pe_v24_client import PEV24Client
from infrastructure.pe_v24.pe_v24_mapper import PEV24Mapper


class PEV24ClientRepository:
    def __init__(self, csv_path: str, csv_repository: CsvRepository | None = None):
        if csv_path is None or not str(csv_path).strip():
            raise ValueError("csv_path must not be empty")

        self._csv_path = str(csv_path).strip()
        self._csv_repository = csv_repository or CsvRepository()
        self._mapper = PEV24Mapper()

    def load_clients(self) -> list[PEV24Client]:
        rows = self._csv_repository.read_rows(self._csv_path)
        return [self._map_row(row) for row in rows]

    def load_client_ids(self) -> list[str]:
        clients = self.load_clients()
        return [client.client_id for client in clients if client.client_id]

    def _map_row(self, row: dict) -> PEV24Client:
        client_id = self._mapper.get_first(
            row,
            ["client_id", "ClientID", "id", "ID", "code", "Code"],
        )

        name = self._mapper.get_first(
            row,
            ["name", "Name", "client_name", "ClientName"],
        )

        cash = self._mapper.get_first(
            row,
            ["cash", "Cash", "remaining_cash", "RemainingCash"],
        )

        return PEV24Client(
            client_id=str(client_id).strip() if client_id is not None else "",
            name=self._mapper.to_text(name),
            cash=self._mapper.to_float(cash),
            raw=row,
        )