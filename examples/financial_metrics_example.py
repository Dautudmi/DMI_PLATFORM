"""
DMI Platform

Financial Metrics Example
"""

from dmi_core.services import FinancialStatementService
from dmi_core.metrics import FinancialMetrics


def main():

    service = FinancialStatementService()

    statement = service.get(
        symbol="AAA",
        period="QUY",
        page_size=4,
    )

    metrics = FinancialMetrics(statement)

    print("=" * 70)
    print("DMI PLATFORM")
    print("Financial Metrics Example")
    print("=" * 70)

    print(f"Symbol   : {statement.symbol}")
    print(f"Year     : {statement.year}")
    print(f"Quarter  : {statement.quarter}")

    print("-" * 70)

    print("PROFITABILITY")

    print(f"ROE             : {metrics.roe().display}")
    print(f"ROA             : {metrics.roa().display}")
    print(f"Gross Margin    : {metrics.gross_margin().display}")
    print(f"Net Margin      : {metrics.net_margin().display}")

    print("-" * 70)

    print("LEVERAGE")

    print(f"Debt / Equity   : {metrics.debt_to_equity().display}")
    print(f"Debt / Assets   : {metrics.debt_to_assets().display}")

    print("-" * 70)

    print("LIQUIDITY")

    print(f"Current Ratio   : {metrics.current_ratio().display}")

    print("-" * 70)

    print("EFFICIENCY")

    print(f"Asset Turnover  : {metrics.asset_turnover().display}")

    print("-" * 70)

    print("PER SHARE")

    print(f"EPS             : {metrics.eps().display}")
    print(f"BVPS            : {metrics.bvps().display}")

    print("=" * 70)

    print("\nALL METRICS")

    for metric in metrics.all():
        print(
            f"{metric.code:<18}"
            f"{metric.display:<12}"
            f"{metric.unit}"
        )


if __name__ == "__main__":
    main()