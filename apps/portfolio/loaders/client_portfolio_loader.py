from pathlib import Path

from apps.portfolio.models.holding import Holding
from apps.portfolio.models.portfolio import Portfolio


class ClientPortfolioLoader:
    """
    Load a client portfolio from a CSV file.

    CSV format:

    Client Name,Anh Dung
    Cash,25000000

    Symbol,Quantity,Average Cost,Current Price
    FPT,100,95000,105000
    MBB,200,24000,27000
    HPG,300,26000,28500
    """

    def load(
        self,
        csv_file: str | Path,
    ) -> Portfolio:

        csv_file = Path(csv_file)

        lines = csv_file.read_text(
            encoding="utf-8"
        ).splitlines()

        client_name = "Unknown"

        cash = 0.0

        holdings: list[Holding] = []

        data_started = False

        for line in lines:

            line = line.strip()

            if not line:
                continue

            parts = [p.strip() for p in line.split(",")]

            if parts[0] == "Client Name":
                client_name = parts[1]
                continue

            if parts[0] == "Cash":
                cash = float(parts[1])
                continue

            if parts[0] == "Symbol":
                data_started = True
                continue

            if not data_started:
                continue

            holdings.append(
                Holding(
                    symbol=parts[0],
                    quantity=float(parts[1]),
                    average_cost=float(parts[2]),
                    current_price=float(parts[3]),
                )
            )

        return Portfolio(
            client_name=client_name,
            cash=cash,
            holdings=holdings,
        )