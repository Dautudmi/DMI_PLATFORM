from datetime import datetime

from apps.portfolio.models.holding import Holding
from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.transaction.buy_transaction import (
    BuyTransaction,
)
from apps.portfolio.transaction.position_engine import (
    PositionEngine,
)
from apps.portfolio.transaction.transaction_service import (
    TransactionService,
)


class FakeTransactionRepository:
    def __init__(self):
        self.records = []

    def append(self, record):
        self.records.append(record)


class FakeClock:
    def now(self):
        return datetime(
            2026,
            7,
            10,
            10,
            30,
            0,
        )


def build_portfolio() -> Portfolio:
    return Portfolio(
        client_name="anh_manh",
        cash=100000,
        holdings=[
            Holding(
                symbol="NAB",
                quantity=1000,
                average_cost=12,
                current_price=13,
            )
        ],
    )


def test_transaction_service_requires_position_engine():
    try:
        TransactionService(
            position_engine=None,
            transaction_repository=(
                FakeTransactionRepository()
            ),
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "position_engine must not be None"
        )
    else:
        assert False


def test_transaction_service_requires_repository():
    try:
        TransactionService(
            position_engine=PositionEngine(),
            transaction_repository=None,
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "transaction_repository must not be None"
        )
    else:
        assert False


def test_transaction_service_applies_and_records_transaction():
    repository = FakeTransactionRepository()

    service = TransactionService(
        position_engine=PositionEngine(),
        transaction_repository=repository,
        clock=FakeClock(),
        trade_id_factory=lambda: "trade-001",
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

    assert result.success is True
    assert result.portfolio is not None
    assert result.portfolio.cash == 98000
    assert len(result.portfolio.holdings) == 2

    assert result.record is not None
    assert result.record.trade_id == "trade-001"
    assert result.record.executed_at == datetime(
        2026,
        7,
        10,
        10,
        30,
        0,
    )
    assert result.record.client_id == "anh_manh"
    assert result.record.transaction_type == "BUY"
    assert result.record.symbol == "FPT"
    assert result.record.quantity == 100
    assert result.record.price == 20
    assert result.record.gross_value == 2000

    assert len(repository.records) == 1


def test_transaction_service_does_not_record_failed_trade():
    repository = FakeTransactionRepository()

    service = TransactionService(
        position_engine=PositionEngine(),
        transaction_repository=repository,
        clock=FakeClock(),
        trade_id_factory=lambda: "trade-001",
    )

    result = service.execute(
        portfolio=Portfolio(
            client_name="anh_manh",
            cash=100,
            holdings=[],
        ),
        transaction=BuyTransaction(
            client_id="anh_manh",
            symbol="FPT",
            quantity=100,
            price=20,
        ),
    )

    assert result.success is False
    assert (
        result.error
        == "insufficient cash for buy transaction"
    )
    assert result.portfolio is None
    assert result.record is None
    assert repository.records == []


def test_transaction_service_returns_failed_when_history_write_fails():
    class FailingRepository:
        def append(self, record):
            raise RuntimeError(
                "history write failed"
            )

    service = TransactionService(
        position_engine=PositionEngine(),
        transaction_repository=FailingRepository(),
        clock=FakeClock(),
        trade_id_factory=lambda: "trade-001",
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
    assert result.record is None
    assert result.error == "history write failed"


def test_transaction_service_uses_transaction_executed_at():
    repository = FakeTransactionRepository()

    service = TransactionService(
        position_engine=PositionEngine(),
        transaction_repository=repository,
        clock=FakeClock(),
        trade_id_factory=lambda: "trade-001",
    )

    executed_at = datetime(
        2026,
        7,
        9,
        14,
        25,
        0,
    )

    result = service.execute(
        portfolio=build_portfolio(),
        transaction=BuyTransaction(
            client_id="anh_manh",
            symbol="FPT",
            quantity=100,
            price=20,
            executed_at=executed_at,
        ),
    )

    assert result.success is True
    assert result.record.executed_at == executed_at