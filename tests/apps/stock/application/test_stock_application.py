from dataclasses import dataclass

from apps.stock.application.stock_application import StockApplication


@dataclass(frozen=True)
class FakeStockRow:
    symbol: str
    close: float


class FakeStockRepository:
    def load_rows(self):
        return [
            FakeStockRow(symbol="FPT", close=100),
            FakeStockRow(symbol="HPG", close=30),
        ]

    def load_symbols(self):
        return ["FPT", "HPG"]


def test_stock_application_requires_repository():
    try:
        StockApplication(stock_repository=None)
    except ValueError as exc:
        assert str(exc) == "stock_repository must not be None"
    else:
        assert False


def test_stock_application_inspect_success():
    app = StockApplication(stock_repository=FakeStockRepository())

    result = app.inspect()

    assert result.success is True
    assert result.total_rows == 2
    assert result.total_symbols == 2
    assert result.error is None
    assert result.data["symbols"] == ["FPT", "HPG"]


def test_stock_application_supports_repository_without_load_symbols():
    class RepositoryWithoutLoadSymbols:
        def load_rows(self):
            return [
                FakeStockRow(symbol="fpt", close=100),
                FakeStockRow(symbol="FPT", close=101),
                FakeStockRow(symbol="hpg", close=30),
            ]

    app = StockApplication(stock_repository=RepositoryWithoutLoadSymbols())

    result = app.inspect()

    assert result.success is True
    assert result.total_rows == 3
    assert result.total_symbols == 2
    assert result.data["symbols"] == ["FPT", "HPG"]


def test_stock_application_supports_dict_rows():
    class DictRowRepository:
        def load_rows(self):
            return [
                {"Symbol": "FPT", "Close": "100"},
                {"Symbol": "HPG", "Close": "30"},
            ]

    app = StockApplication(stock_repository=DictRowRepository())

    result = app.inspect()

    assert result.success is True
    assert result.total_rows == 2
    assert result.total_symbols == 2
    assert result.data["symbols"] == ["FPT", "HPG"]


def test_stock_application_returns_failed_when_repository_invalid():
    class InvalidRepository:
        pass

    app = StockApplication(stock_repository=InvalidRepository())

    result = app.inspect()

    assert result.success is False
    assert result.total_rows == 0
    assert result.total_symbols == 0
    assert result.data is None
    assert result.error == "stock_repository must have load_rows method"


def test_stock_application_returns_failed_when_repository_raises():
    class FailingRepository:
        def load_rows(self):
            raise RuntimeError("repository failed")

    app = StockApplication(stock_repository=FailingRepository())

    result = app.inspect()

    assert result.success is False
    assert result.total_rows == 0
    assert result.total_symbols == 0
    assert result.data is None
    assert result.error == "repository failed"