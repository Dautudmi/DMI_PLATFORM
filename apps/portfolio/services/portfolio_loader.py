import csv

from apps.portfolio.models import Holding, Portfolio


class PortfolioLoader:
    """
    Load portfolio from CSV file.
    """

    @staticmethod
    def from_csv(
        file_path: str,
        client_name: str,
        cash: float = 0.0,
    ) -> Portfolio:

        portfolio = Portfolio(
            client_name=client_name,
            cash=cash,
        )

        with open(file_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                portfolio.holdings.append(
                    Holding(
                        symbol=row["symbol"].strip().upper(),
                        quantity=float(row["quantity"]),
                        average_cost=float(row["average_cost"]),
                    )
                )

        return portfolio
        