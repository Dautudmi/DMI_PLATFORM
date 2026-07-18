from datetime import datetime

from infrastructure.portfolio.transaction_csv_repository import (
    TransactionCsvRepository,
)
from infrastructure.portfolio.transaction_record import (
    TransactionRecord,
)


def build_record(
    trade_id: str = "trade-001",
    client_id: str = "anh_manh",
) -> TransactionRecord:
    return TransactionRecord(
        trade_id=trade_id,
        executed_at=datetime(
            2026,
            7,
            10,
            9,
            15,
            30,
        ),
        client_id=client_id,
        transaction_type="BUY",
        symbol="NAB",
        quantity=1000,
        price=12.3,
        gross_value=12300,
    )


def test_transaction_csv_repository_requires_path():
    try:
        TransactionCsvRepository(csv_path="")
    except ValueError as exc:
        assert str(exc) == "csv_path must not be empty"
    else:
        assert False


def test_transaction_csv_repository_returns_empty_when_missing(
    tmp_path,
):
    repository = TransactionCsvRepository(
        csv_path=str(tmp_path / "trade_history.csv")
    )

    assert repository.load_all() == []


def test_transaction_csv_repository_appends_and_loads_record(
    tmp_path,
):
    file_path = tmp_path / "trade_history.csv"

    repository = TransactionCsvRepository(
        csv_path=str(file_path)
    )

    repository.append(build_record())

    records = repository.load_all()

    assert len(records) == 1

    record = records[0]

    assert record.trade_id == "trade-001"
    assert record.client_id == "anh_manh"
    assert record.transaction_type == "BUY"
    assert record.symbol == "NAB"
    assert record.quantity == 1000
    assert record.price == 12.3
    assert record.gross_value == 12300


def test_transaction_csv_repository_does_not_duplicate_header(
    tmp_path,
):
    file_path = tmp_path / "trade_history.csv"

    repository = TransactionCsvRepository(
        csv_path=str(file_path)
    )

    repository.append(
        build_record(trade_id="trade-001")
    )
    repository.append(
        build_record(trade_id="trade-002")
    )

    text = file_path.read_text(
        encoding="utf-8-sig"
    )

    assert text.count(
        "TradeId,Time,Client,Type,"
        "Symbol,Quantity,Price,Value"
    ) == 1

    assert len(repository.load_all()) == 2


def test_transaction_csv_repository_loads_by_client_id(
    tmp_path,
):
    repository = TransactionCsvRepository(
        csv_path=str(
            tmp_path / "trade_history.csv"
        )
    )

    repository.append(
        build_record(
            trade_id="trade-001",
            client_id="anh_manh",
        )
    )
    repository.append(
        build_record(
            trade_id="trade-002",
            client_id="anh_dung",
        )
    )

    records = repository.load_by_client_id(
        "anh_manh"
    )

    assert len(records) == 1
    assert records[0].trade_id == "trade-001"


def test_transaction_csv_repository_contains_trade_id(
    tmp_path,
):
    repository = TransactionCsvRepository(
        csv_path=str(
            tmp_path / "trade_history.csv"
        )
    )

    repository.append(build_record())

    assert repository.contains_trade_id(
        "trade-001"
    ) is True

    assert repository.contains_trade_id(
        "trade-999"
    ) is False