from dataclasses import dataclass

from apps.portfolio.models.holding import Holding
from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.transaction.buy_transaction import (
    BuyTransaction,
)
from apps.portfolio.transaction.portfolio_transaction_service import (
    PortfolioTransactionService,
)


@dataclass
class FakeTransactionResult:
    success: bool
    portfolio: Portfolio | None = None
    record: object | None = None
    error: str | None = None


@dataclass
class FakeWriteResult:
    success: bool
    error: str | None = None


class FakeTransactionService:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def execute(self, portfolio, transaction):
        self.calls.append(
            {
                "portfolio": portfolio,
                "transaction": transaction,
            }
        )
        return self.result


class FakePortfolioWriter:
    def __init__(self, result):
        self.result = result
        self.portfolios = []

    def write(self, portfolio):
        self.portfolios.append(portfolio)
        return self.result


def build_portfolio() -> Portfolio:
    return Portfolio(
        client_name="anh_manh",
        cash=100000,
        holdings=[
            Holding(
                symbol="NAB",
                quantity=1000,
                average_cost=12,
            )
        ],
    )


def test_portfolio_transaction_service_requires_transaction_service():
    try:
        PortfolioTransactionService(
            transaction_service=None,
            portfolio_writer=FakePortfolioWriter(
                FakeWriteResult(success=True)
            ),
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "transaction_service must not be None"
        )
    else:
        assert False


def test_portfolio_transaction_service_requires_writer():
    try:
        PortfolioTransactionService(
            transaction_service=FakeTransactionService(
                FakeTransactionResult(
                    success=True
                )
            ),
            portfolio_writer=None,
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "portfolio_writer must not be None"
        )
    else:
        assert False


def test_portfolio_transaction_service_executes_and_writes():
    updated_portfolio = build_portfolio()
    updated_portfolio.cash = 98000

    transaction_record = object()

    transaction_service = FakeTransactionService(
        FakeTransactionResult(
            success=True,
            portfolio=updated_portfolio,
            record=transaction_record,
        )
    )

    write_result = FakeWriteResult(
        success=True
    )

    writer = FakePortfolioWriter(
        write_result
    )

    service = PortfolioTransactionService(
        transaction_service=transaction_service,
        portfolio_writer=writer,
    )

    transaction = BuyTransaction(
        client_id="anh_manh",
        symbol="FPT",
        quantity=100,
        price=20,
    )

    result = service.execute(
        portfolio=build_portfolio(),
        transaction=transaction,
    )

    assert result.success is True
    assert result.portfolio is updated_portfolio
    assert result.record is transaction_record
    assert result.write_result is write_result
    assert result.error is None

    assert len(writer.portfolios) == 1
    assert (
        writer.portfolios[0]
        is updated_portfolio
    )


def test_portfolio_transaction_service_does_not_write_failed_transaction():
    transaction_service = FakeTransactionService(
        FakeTransactionResult(
            success=False,
            portfolio=None,
            record=None,
            error="transaction failed",
        )
    )

    writer = FakePortfolioWriter(
        FakeWriteResult(success=True)
    )

    service = PortfolioTransactionService(
        transaction_service=transaction_service,
        portfolio_writer=writer,
    )

    result = service.execute(
        portfolio=build_portfolio(),
        transaction=BuyTransaction(
            client_id="anh_manh",
            symbol="FPT",
            quantity=100,
            price=20,
        ),
    )

    assert result.success is False
    assert result.error == "transaction failed"
    assert writer.portfolios == []


def test_portfolio_transaction_service_returns_failed_when_write_fails():
    updated_portfolio = build_portfolio()

    transaction_service = FakeTransactionService(
        FakeTransactionResult(
            success=True,
            portfolio=updated_portfolio,
            record=object(),
            error=None,
        )
    )

    writer = FakePortfolioWriter(
        FakeWriteResult(
            success=False,
            error="portfolio write failed",
        )
    )

    service = PortfolioTransactionService(
        transaction_service=transaction_service,
        portfolio_writer=writer,
    )

    result = service.execute(
        portfolio=build_portfolio(),
        transaction=BuyTransaction(
            client_id="anh_manh",
            symbol="FPT",
            quantity=100,
            price=20,
        ),
    )

    assert result.success is False
    assert result.portfolio is None
    assert result.error == (
        "portfolio write failed"
    )
    assert result.write_result is not None