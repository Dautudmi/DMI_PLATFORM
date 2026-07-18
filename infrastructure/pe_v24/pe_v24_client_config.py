from dataclasses import dataclass


@dataclass(frozen=True)
class PEV24ClientConfig:
    """
    Cấu hình một khách hàng trong client_config.csv.
    """

    client_id: str
    capital: float
    cash_percent: float
    raw: dict | None = None