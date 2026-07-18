from apps.portfolio.models.holding import Holding
from apps.portfolio.models.portfolio import Portfolio
from apps.portfolio.transaction.buy_transaction import (
    BuyTransaction,
)
from apps.portfolio.transaction.position_engine import (
    PositionEngine,
)
from apps.portfolio.transaction.sell_transaction import (
    SellTransaction,
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


def test_position_engine_requires_portfolio():
    engine = PositionEngine()

    transaction = BuyTransaction(
        client_id="anh_manh",
        symbol="NAB",
        quantity=100,
        price=13,
    )

    try:
        engine.apply(
            portfolio=None,
            transaction=transaction,
        )
    except ValueError as exc:
        assert str(exc) == "portfolio must not be None"
    else:
        assert False


def test_position_engine_requires_transaction():
    engine = PositionEngine()

    try:
        engine.apply(
            portfolio=build_portfolio(),
            transaction=None,
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "transaction must not be None"
        )
    else:
        assert False


def test_position_engine_rejects_client_mismatch():
    engine = PositionEngine()

    result = engine.apply(
        portfolio=build_portfolio(),
        transaction=BuyTransaction(
            client_id="anh_dung",
            symbol="NAB",
            quantity=100,
            price=13,
        ),
    )

    assert result.success is False
    assert (
        result.error
        == "transaction client_id does not match "
        "portfolio client_name"
    )


def test_position_engine_adds_new_holding():
    engine = PositionEngine()
    original = build_portfolio()

    result = engine.apply(
        portfolio=original,
        transaction=BuyTransaction(
            client_id="anh_manh",
            symbol="FPT",
            quantity=200,
            price=20,
        ),
    )

    assert result.success is True
    assert result.portfolio is not None
    assert len(result.portfolio.holdings) == 2
    assert result.portfolio.cash == 96000

    holding = result.portfolio.holdings[1]

    assert holding.symbol == "FPT"
    assert holding.quantity == 200
    assert holding.average_cost == 20

    assert len(original.holdings) == 1
    assert original.cash == 100000


def test_position_engine_buy_updates_average_cost():
    engine = PositionEngine()

    result = engine.apply(
        portfolio=build_portfolio(),
        transaction=BuyTransaction(
            client_id="anh_manh",
            symbol="NAB",
            quantity=1000,
            price=14,
        ),
    )

    assert result.success is True

    holding = result.portfolio.holdings[0]

    assert holding.quantity == 2000
    assert holding.average_cost == 13
    assert result.portfolio.cash == 86000


def test_position_engine_rejects_buy_when_cash_insufficient():
    engine = PositionEngine()

    result = engine.apply(
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


def test_position_engine_sells_partial_holding():
    engine = PositionEngine()

    result = engine.apply(
        portfolio=build_portfolio(),
        transaction=SellTransaction(
            client_id="anh_manh",
            symbol="NAB",
            quantity=400,
            price=13,
        ),
    )

    assert result.success is True

    holding = result.portfolio.holdings[0]

    assert holding.quantity == 600
    assert holding.average_cost == 12
    assert result.portfolio.cash == 105200


def test_position_engine_sells_entire_holding():
    engine = PositionEngine()

    result = engine.apply(
        portfolio=build_portfolio(),
        transaction=SellTransaction(
            client_id="anh_manh",
            symbol="NAB",
            quantity=1000,
            price=13,
        ),
    )

    assert result.success is True
    assert result.portfolio.holdings == []
    assert result.portfolio.cash == 113000


def test_position_engine_rejects_sell_when_holding_missing():
    engine = PositionEngine()

    result = engine.apply(
        portfolio=build_portfolio(),
        transaction=SellTransaction(
            client_id="anh_manh",
            symbol="FPT",
            quantity=100,
            price=20,
        ),
    )

    assert result.success is False
    assert (
        result.error
        == "holding not found for symbol FPT"
    )


def test_position_engine_rejects_sell_quantity_too_large():
    engine = PositionEngine()

    result = engine.apply(
        portfolio=build_portfolio(),
        transaction=SellTransaction(
            client_id="anh_manh",
            symbol="NAB",
            quantity=1500,
            price=13,
        ),
    )

    assert result.success is False
    assert (
        result.error
        == "insufficient holding quantity "
        "for sell transaction"
    )