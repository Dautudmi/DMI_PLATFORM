from dataclasses import dataclass


@dataclass(frozen=True)
class PEV24Client:
    client_id: str
    name: str | None = None
    cash: float | None = None
    raw: dict | None = None