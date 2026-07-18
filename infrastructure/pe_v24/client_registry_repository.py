from infrastructure.csv_repository import CsvRepository
from infrastructure.pe_v24.pe_v24_client_config import PEV24ClientConfig
from infrastructure.pe_v24.pe_v24_mapper import PEV24Mapper


class PEV24ClientRegistryRepository:
    """
    Repository đọc client_config.csv của PE_V2.4.

    Cấu trúc file thực tế:

    Client,Capital,CashPercent
    anh_dung,1000000000,0
    anh_manh,300000000,0

    Responsibility:
    - đọc danh sách khách hàng
    - map dữ liệu thành PEV24ClientConfig
    - tra cứu cấu hình theo client_id

    Không đọc danh mục cổ phiếu.
    Không tính toán portfolio.
    Không render báo cáo.
    """

    def __init__(
        self,
        csv_path: str,
        csv_repository: CsvRepository | None = None,
    ):
        if csv_path is None or not str(csv_path).strip():
            raise ValueError("csv_path must not be empty")

        self._csv_path = str(csv_path).strip()
        self._csv_repository = csv_repository or CsvRepository()
        self._mapper = PEV24Mapper()

    @property
    def csv_path(self) -> str:
        return self._csv_path

    def load_clients(self) -> list[PEV24ClientConfig]:
        rows = self._csv_repository.read_rows(self._csv_path)

        clients: list[PEV24ClientConfig] = []

        for row in rows:
            client = self._map_row(row)

            if client.client_id:
                clients.append(client)

        return clients

    def load_client_ids(self) -> list[str]:
        return [client.client_id for client in self.load_clients()]

    def find_by_id(self, client_id: str) -> PEV24ClientConfig | None:
        normalized_client_id = self._normalize_client_id(client_id)

        for client in self.load_clients():
            if client.client_id == normalized_client_id:
                return client

        return None

    def require_by_id(self, client_id: str) -> PEV24ClientConfig:
        normalized_client_id = self._normalize_client_id(client_id)
        client = self.find_by_id(normalized_client_id)

        if client is None:
            raise KeyError(f"Client not found: {normalized_client_id}")

        return client

    def _map_row(self, row: dict) -> PEV24ClientConfig:
        client_id = self._mapper.get_first(
            row,
            [
                "Client",
                "client",
                "client_id",
                "ClientID",
                "ClientId",
            ],
        )

        capital = self._mapper.get_first(
            row,
            [
                "Capital",
                "capital",
                "TotalCapital",
                "total_capital",
            ],
        )

        cash_percent = self._mapper.get_first(
            row,
            [
                "CashPercent",
                "cash_percent",
                "Cash_Percent",
                "cashPercent",
            ],
        )

        normalized_client_id = (
            str(client_id).strip()
            if client_id is not None
            else ""
        )

        normalized_capital = self._mapper.to_float(capital)
        normalized_cash_percent = self._mapper.to_float(cash_percent)

        return PEV24ClientConfig(
            client_id=normalized_client_id,
            capital=normalized_capital if normalized_capital is not None else 0.0,
            cash_percent=(
                normalized_cash_percent
                if normalized_cash_percent is not None
                else 0.0
            ),
            raw=row,
        )

    def _normalize_client_id(self, client_id: str) -> str:
        if client_id is None or not str(client_id).strip():
            raise ValueError("client_id must not be empty")

        return str(client_id).strip()