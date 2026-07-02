"""
DMI Platform

Financial Analysis Example
"""

from dmi_core.analysis import FinancialAnalysis
from dmi_core.services import FinancialStatementService


def main():

    service = FinancialStatementService()

    statement = service.get(
        symbol="AAA",
        period="QUY",
        page_size=4,
    )

    analysis = FinancialAnalysis(statement)

    result = analysis.analyze()

    print("=" * 70)
    print("DMI PLATFORM")
    print("Financial Analysis Example")
    print("=" * 70)

    print(f"Symbol   : {statement.symbol}")
    print(f"Year     : {statement.year}")
    print(f"Quarter  : {statement.quarter}")

    print("-" * 70)

    print("PROFITABILITY")

    print(f"Rating         : {result.profitability.rating}")
    print(f"Score          : {result.profitability.score}")
    print(f"Summary        : {result.profitability.summary}")
    print(f"Recommendation : {result.profitability.recommendation}")

    print("-" * 70)

    print("LEVERAGE")

    print(f"Rating         : {result.leverage.rating}")
    print(f"Score          : {result.leverage.score}")
    print(f"Summary        : {result.leverage.summary}")
    print(f"Recommendation : {result.leverage.recommendation}")

    print("-" * 70)

    print("OVERALL RESULT")

    print(f"Overall Score  : {result.overall_score:.1f}")
    print(f"Overall Rating : {result.overall_rating}")
    print(f"Recommendation : {result.recommendation}")

    print("=" * 70)

    print("\nSUMMARY")

    for item in analysis.summary():
        print(
            f"{item.code:<18}"
            f"{item.rating:<12}"
            f"{item.score:<6}"
            f"{item.summary}"
        )


if __name__ == "__main__":
    main()