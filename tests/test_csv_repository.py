from infrastructure.csv_repository import CsvRepository


def test_write_and_read_rows(tmp_path):
    repo = CsvRepository()

    rows = [
        {"symbol": "FPT", "price": "100"},
        {"symbol": "HPG", "price": "30"},
    ]

    file_path = tmp_path / "data.csv"

    repo.write_rows(str(file_path), rows)

    loaded = repo.read_rows(str(file_path))

    assert loaded == rows


def test_none_rows_raise_error(tmp_path):
    repo = CsvRepository()

    try:
        repo.write_rows(str(tmp_path / "data.csv"), None)
    except ValueError as exc:
        assert str(exc) == "rows must not be None"
    else:
        assert False


def test_missing_file_raise_error(tmp_path):
    repo = CsvRepository()

    try:
        repo.read_rows(str(tmp_path / "missing.csv"))
    except FileNotFoundError:
        assert True
    else:
        assert False