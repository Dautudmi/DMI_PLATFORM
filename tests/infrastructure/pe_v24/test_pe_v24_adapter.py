from infrastructure.pe_v24.pe_v24_adapter import PEV24Adapter
from infrastructure.pe_v24.pe_v24_cafef_repository import PEV24CafeFRepository
from infrastructure.pe_v24.pe_v24_paths import PEV24Paths


def test_pe_v24_adapter_requires_repository():
    try:
        PEV24Adapter(cafef_repository=None)
    except ValueError as exc:
        assert str(exc) == "cafef_repository must not be None"
    else:
        assert False


def test_pe_v24_adapter_inspect_success(tmp_path):
    file_path = tmp_path / "cafef_all.csv"

    file_path.write_text(
        "Symbol,Date,Close,Volume\n"
        "FPT,2026-07-09,100,1000000\n"
        "HPG,2026-07-09,30,2000000\n",
        encoding="utf-8-sig",
    )

    repo = PEV24CafeFRepository(
        paths=PEV24Paths(cafef_all_csv_path=str(file_path)),
    )

    adapter = PEV24Adapter(cafef_repository=repo)

    result = adapter.inspect()

    assert result.success is True
    assert result.total_rows == 2
    assert result.total_symbols == 2
    assert result.error is None
    assert result.data["symbols"] == ["FPT", "HPG"]


def test_pe_v24_adapter_inspect_failed_when_file_missing(tmp_path):
    repo = PEV24CafeFRepository(
        paths=PEV24Paths(cafef_all_csv_path=str(tmp_path / "missing.csv")),
    )

    adapter = PEV24Adapter(cafef_repository=repo)

    result = adapter.inspect()

    assert result.success is False
    assert result.total_rows == 0
    assert result.total_symbols == 0
    assert result.data is None
    assert "CSV file not found" in result.error