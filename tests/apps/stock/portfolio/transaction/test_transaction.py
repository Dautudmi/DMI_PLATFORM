from apps.portfolio.transaction.buy_transaction import (
    BuyTransaction,
)
from apps.portfolio.transaction.sell_transaction import (
    SellTransaction,
)
from apps.portfolio.transaction.transaction_type import (
    TransactionType,
)


def test_buy_transaction_normalizes_values():
    transaction = BuyTransaction(
        client_id=" anh_manh ",
        symbol=" nab ",
        quantity=100,
        price=12.5,
    )

    assert transaction.client_id == "anh_manh"
    assert transaction.symbol == "NAB"
    assert transaction.quantity == 100
    assert transaction.price == 12.5
    assert (
        transaction.transaction_type
        == TransactionType.BUY
    )
    assert transaction.gross_value == 1250


def test_sell_transaction_has_sell_type():
    transaction = SellTransaction(
        client_id="anh_manh",
        symbol="NAB",
        quantity=50,
        price=13,
    )

    assert (
        transaction.transaction_type
        == TransactionType.SELL
    )
    assert transaction.gross_value == 650


def test_transaction_rejects_empty_client_id():
    try:
        BuyTransaction(
            client_id="",
            symbol="NAB",
            quantity=100,
            price=12.5,
        )
    except ValueError as exc:
        assert str(exc) == "client_id must not be empty"
    else:
        assert False


def test_transaction_rejects_empty_symbol():
    try:
        BuyTransaction(
            client_id="anh_manh",
            symbol="",
            quantity=100,
            price=12.5,
        )
    except ValueError as exc:
        assert str(exc) == "symbol must not be empty"
    else:
        assert False


def test_transaction_rejects_zero_quantity():
    try:
        BuyTransaction(
            client_id="anh_manh",
            symbol="NAB",
            quantity=0,
            price=12.5,
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "quantity must be greater than 0"
        )
    else:
        assert False


def test_transaction_rejects_negative_price():
    try:
        BuyTransaction(
            client_id="anh_manh",
            symbol="NAB",
            quantity=100,
            price=-1,
        )
    except ValueError as exc:
        assert str(exc) == "price must not be negative"
    else:
        assert False