from dataclasses import dataclass, field

from .holding import Holding


@dataclass(slots=True)
class Portfolio:
    """
    Client investment portfolio.
    """

    client_name: str

    cash: float = 0.0

    holdings: list[Holding] = field(default_factory=list)

    total_value: float = 0.0