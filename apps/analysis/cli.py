from __future__ import annotations

import argparse
import sys

from apps.analysis.analysis_pipeline import AnalysisPipeline
from dmi_core.providers.cafef_provider import CafeFProvider
from dmi_core.providers.financial_statement_provider import (
    FinancialStatementProvider,
)


def build_pipeline() -> AnalysisPipeline:
    provider = FinancialStatementProvider(
        provider=CafeFProvider(),
        provider_name="CafeF",
    )

    return AnalysisPipeline(
        statement_provider=provider,
    )


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="analysis",
        description="DMI Framework Analysis CLI",
    )

    parser.add_argument(
        "symbol",
        help="Stock symbol (FPT, HPG, MBB...)",
    )

    parser.add_argument(
        "--price",
        type=float,
        default=None,
        help="Current market price",
    )

    parser.add_argument(
        "--period",
        default="NAM",
        choices=[
            "NAM",
            "QUY",
        ],
        help="Financial period",
    )

    parser.add_argument(
        "--page-size",
        type=int,
        default=4,
    )

    return parser


def main() -> int:
    parser = create_parser()

    args = parser.parse_args()

    pipeline = build_pipeline()

    result = pipeline.run(
        symbol=args.symbol,
        current_price=args.price,
        period=args.period,
        page_size=args.page_size,
    )
    print("\n===== RAW MODEL DEBUG =====")

    bs = result.statement.balance_sheet
    is_ = result.statement.income_statement

    print("Equity           :", bs.equity)
    print("Charter Capital  :", bs.charter_capital)
    print("EPS              :", is_.eps)
    print("EBITDA           :", is_.ebitda)

    print("\n===== VALUATION =====")

    for v in result.valuation_result:
        print(
            v.method,
            v.intrinsic_value,
            v.description,
        )

    print(
        pipeline.explain_result(
            result
        )
    )

    if result.succeeded:
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())