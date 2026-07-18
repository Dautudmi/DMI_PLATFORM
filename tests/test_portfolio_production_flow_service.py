from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from apps.portfolio.models.holding import Holding
from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.services.portfolio_production_flow_service import (
    PortfolioProductionFlowService,
)
from apps.portfolio.transaction.portfolio_transaction_result import (
    PortfolioTransactionResult,
)
from infrastructure.pe_v24.pe_v24_portfolio_write_result import (
    PEV24PortfolioWriteResult,
)


@dataclass
class FakeTransaction:
    transaction_type: Any
    symbol: str


@dataclass
class FakeTransactionType:
    value: str


class FakePortfolioTransactionService:
    def __init__(
        self,
        result: PortfolioTransactionResult,
    ) -> None:
        self._result = result
        self.calls: list[dict[str, Any]] = []

    def execute(
        self,
        portfolio: Portfolio,
        transaction: Any,
    ) -> PortfolioTransactionResult:
        self.calls.append(
            {
                "portfolio": portfolio,
                "transaction": transaction,
            }
        )

        return self._result


class FakeDailyPortfolioReportService:
    def __init__(
        self,
        report_text: str = "PORTFOLIO REPORT",
    ) -> None:
        self._report_text = report_text
        self.calls: list[str] = []

    def generate(
        self,
        csv_file: str | Path,
    ) -> str:
        self.calls.append(str(csv_file))

        return self._report_text


def create_portfolio() -> Portfolio:
    return Portfolio(
        client_name="anh_dung",
        cash=25_000_000,
        holdings=[
            Holding(
                symbol="NAB",
                quantity=1_200,
                average_cost=12.45,
                current_price=None,
            )
        ],
    )


def create_transaction() -> FakeTransaction:
    return FakeTransaction(
        transaction_type=FakeTransactionType(
            value="BUY"
        ),
        symbol="FTS",
    )


def create_success_transaction_result(
    portfolio: Portfolio,
    transaction: Any,
    file_path: str,
) -> PortfolioTransactionResult:
    write_result = PEV24PortfolioWriteResult(
        success=True,
        client_id=portfolio.client_name,
        file_path=file_path,
        total_positions=len(portfolio.holdings),
        backup_path=None,
        error=None,
    )

    return PortfolioTransactionResult(
        success=True,
        transaction=transaction,
        portfolio=portfolio,
        record=None,
        write_result=write_result,
        message="transaction completed",
        error=None,
    )


def test_constructor_rejects_none_transaction_service() -> None:
    report_service = FakeDailyPortfolioReportService()

    with pytest.raises(
        ValueError,
        match=(
            "portfolio_transaction_service "
            "must not be None"
        ),
    ):
        PortfolioProductionFlowService(
            portfolio_transaction_service=None,
            daily_portfolio_report_service=report_service,
        )


def test_constructor_rejects_none_report_service() -> None:
    transaction_service = FakePortfolioTransactionService(
        result=None,
    )

    with pytest.raises(
        ValueError,
        match=(
            "daily_portfolio_report_service "
            "must not be None"
        ),
    ):
        PortfolioProductionFlowService(
            portfolio_transaction_service=transaction_service,
            daily_portfolio_report_service=None,
        )


def test_execute_rejects_none_portfolio() -> None:
    transaction = create_transaction()

    transaction_service = FakePortfolioTransactionService(
        result=None,
    )

    report_service = FakeDailyPortfolioReportService()

    service = PortfolioProductionFlowService(
        portfolio_transaction_service=transaction_service,
        daily_portfolio_report_service=report_service,
    )

    with pytest.raises(
        ValueError,
        match="portfolio must not be None",
    ):
        service.execute(
            portfolio=None,
            transaction=transaction,
        )


def test_execute_rejects_none_transaction() -> None:
    portfolio = create_portfolio()

    transaction_service = FakePortfolioTransactionService(
        result=None,
    )

    report_service = FakeDailyPortfolioReportService()

    service = PortfolioProductionFlowService(
        portfolio_transaction_service=transaction_service,
        daily_portfolio_report_service=report_service,
    )

    with pytest.raises(
        ValueError,
        match="transaction must not be None",
    ):
        service.execute(
            portfolio=portfolio,
            transaction=None,
        )


def test_execute_returns_successful_production_result(
    tmp_path: Path,
) -> None:
    portfolio = create_portfolio()
    transaction = create_transaction()

    portfolio_file_path = (
        tmp_path / "client_anh_dung.csv"
    )

    transaction_result = (
        create_success_transaction_result(
            portfolio=portfolio,
            transaction=transaction,
            file_path=str(portfolio_file_path),
        )
    )

    transaction_service = FakePortfolioTransactionService(
        result=transaction_result,
    )

    report_service = FakeDailyPortfolioReportService(
        report_text="TELEGRAM PORTFOLIO REPORT"
    )

    service = PortfolioProductionFlowService(
        portfolio_transaction_service=transaction_service,
        daily_portfolio_report_service=report_service,
    )

    result = service.execute(
        portfolio=portfolio,
        transaction=transaction,
    )

    assert result.success is True
    assert result.transaction is transaction
    assert result.portfolio is portfolio
    assert result.transaction_result is transaction_result
    assert result.portfolio_file_path == str(
        portfolio_file_path
    )
    assert (
        result.report_text
        == "TELEGRAM PORTFOLIO REPORT"
    )
    assert result.message is not None
    assert "anh_dung" in result.message
    assert result.error is None

    assert len(transaction_service.calls) == 1
    assert (
        transaction_service.calls[0]["portfolio"]
        is portfolio
    )
    assert (
        transaction_service.calls[0]["transaction"]
        is transaction
    )

    assert report_service.calls == [
        str(portfolio_file_path)
    ]


def test_execute_stops_when_transaction_flow_fails() -> None:
    portfolio = create_portfolio()
    transaction = create_transaction()

    failed_transaction_result = PortfolioTransactionResult(
        success=False,
        transaction=transaction,
        portfolio=None,
        record=None,
        write_result=None,
        message=None,
        error="insufficient cash",
    )

    transaction_service = FakePortfolioTransactionService(
        result=failed_transaction_result,
    )

    report_service = FakeDailyPortfolioReportService()

    service = PortfolioProductionFlowService(
        portfolio_transaction_service=transaction_service,
        daily_portfolio_report_service=report_service,
    )

    result = service.execute(
        portfolio=portfolio,
        transaction=transaction,
    )

    assert result.success is False
    assert result.transaction is transaction
    assert result.portfolio is None
    assert (
        result.transaction_result
        is failed_transaction_result
    )
    assert result.portfolio_file_path is None
    assert result.report_text is None
    assert result.message is None
    assert result.error == "insufficient cash"

    assert report_service.calls == []


def test_execute_fails_when_updated_portfolio_is_missing(
    tmp_path: Path,
) -> None:
    portfolio = create_portfolio()
    transaction = create_transaction()

    write_result = PEV24PortfolioWriteResult(
        success=True,
        client_id="anh_dung",
        file_path=str(
            tmp_path / "client_anh_dung.csv"
        ),
        total_positions=1,
        backup_path=None,
        error=None,
    )

    transaction_result = PortfolioTransactionResult(
        success=True,
        transaction=transaction,
        portfolio=None,
        record=None,
        write_result=write_result,
        message="transaction completed",
        error=None,
    )

    transaction_service = FakePortfolioTransactionService(
        result=transaction_result,
    )

    report_service = FakeDailyPortfolioReportService()

    service = PortfolioProductionFlowService(
        portfolio_transaction_service=transaction_service,
        daily_portfolio_report_service=report_service,
    )

    result = service.execute(
        portfolio=portfolio,
        transaction=transaction,
    )

    assert result.success is False
    assert result.portfolio is None
    assert result.report_text is None
    assert result.error is not None
    assert "returned no portfolio" in result.error

    assert report_service.calls == []


def test_execute_fails_when_write_result_is_missing() -> None:
    portfolio = create_portfolio()
    transaction = create_transaction()

    transaction_result = PortfolioTransactionResult(
        success=True,
        transaction=transaction,
        portfolio=portfolio,
        record=None,
        write_result=None,
        message="transaction completed",
        error=None,
    )

    transaction_service = FakePortfolioTransactionService(
        result=transaction_result,
    )

    report_service = FakeDailyPortfolioReportService()

    service = PortfolioProductionFlowService(
        portfolio_transaction_service=transaction_service,
        daily_portfolio_report_service=report_service,
    )

    result = service.execute(
        portfolio=portfolio,
        transaction=transaction,
    )

    assert result.success is False
    assert result.portfolio is portfolio
    assert result.report_text is None
    assert result.error is not None
    assert "returned no write result" in result.error

    assert report_service.calls == []


def test_execute_fails_when_report_is_empty(
    tmp_path: Path,
) -> None:
    portfolio = create_portfolio()
    transaction = create_transaction()

    portfolio_file_path = (
        tmp_path / "client_anh_dung.csv"
    )

    transaction_result = (
        create_success_transaction_result(
            portfolio=portfolio,
            transaction=transaction,
            file_path=str(portfolio_file_path),
        )
    )

    transaction_service = FakePortfolioTransactionService(
        result=transaction_result,
    )

    report_service = FakeDailyPortfolioReportService(
        report_text="   "
    )

    service = PortfolioProductionFlowService(
        portfolio_transaction_service=transaction_service,
        daily_portfolio_report_service=report_service,
    )

    result = service.execute(
        portfolio=portfolio,
        transaction=transaction,
    )

    assert result.success is False
    assert result.portfolio is portfolio
    assert (
        result.portfolio_file_path
        == str(portfolio_file_path)
    )
    assert result.report_text is None
    assert result.error is not None
    assert "returned empty report" in result.error


def test_execute_converts_unexpected_exception_to_result() -> None:
    portfolio = create_portfolio()
    transaction = create_transaction()

    class BrokenTransactionService:
        def execute(
            self,
            portfolio: Portfolio,
            transaction: Any,
        ) -> Any:
            raise RuntimeError("unexpected production error")

    report_service = FakeDailyPortfolioReportService()

    service = PortfolioProductionFlowService(
        portfolio_transaction_service=(
            BrokenTransactionService()
        ),
        daily_portfolio_report_service=report_service,
    )

    result = service.execute(
        portfolio=portfolio,
        transaction=transaction,
    )

    assert result.success is False
    assert result.transaction is transaction
    assert result.portfolio is None
    assert result.transaction_result is None
    assert result.report_text is None
    assert (
        result.error
        == "unexpected production error"
    )

    assert report_service.calls == []