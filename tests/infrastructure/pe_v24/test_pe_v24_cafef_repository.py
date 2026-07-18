from infrastructure.pe_v24.pe_v24_paths import PEV24Paths
from infrastructure.pe_v24.pe_v24_cafef_repository import PEV24CafeFRepository


def test_pe_v24_cafef_repository_load_rows(tmp_path):
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

    rows = repo.load_rows()

    assert len(rows) == 2
    assert rows[0].symbol == "FPT"
    assert rows[0].date == "2026-07-09"
    assert rows[0].close == 100
    assert rows[0].volume == 1000000


def test_pe_v24_cafef_repository_load_symbols_unique(tmp_path):
    file_path = tmp_path / "cafef_all.csv"

    file_path.write_text(
        "Symbol,Date,Close,Volume\n"
        "FPT,2026-07-08,99,900000\n"
        "FPT,2026-07-09,100,1000000\n"
        "HPG,2026-07-09,30,2000000\n",
        encoding="utf-8-sig",
    )

    repo = PEV24CafeFRepository(
        paths=PEV24Paths(cafef_all_csv_path=str(file_path)),
    )

    symbols = repo.load_symbols()

    assert symbols == ["FPT", "HPG"]


def test_pe_v24_cafef_repository_load_latest_by_symbol(tmp_path):
    file_path = tmp_path / "cafef_all.csv"

    file_path.write_text(
        "Symbol,Date,Close,Volume\n"
        "FPT,2026-07-08,99,900000\n"
        "FPT,2026-07-09,100,1000000\n"
        "HPG,2026-07-09,30,2000000\n",
        encoding="utf-8-sig",
    )

    repo = PEV24CafeFRepository(
        paths=PEV24Paths(cafef_all_csv_path=str(file_path)),
    )

    latest = repo.load_latest_by_symbol()

    assert latest["FPT"].date == "2026-07-09"
    assert latest["FPT"].close == 100
    assert latest["HPG"].close == 30


def test_pe_v24_cafef_repository_accepts_lowercase_columns(tmp_path):
    file_path = tmp_path / "cafef_all.csv"

    file_path.write_text(
        "symbol,date,close,volume\n"
        "fpt,2026-07-09,100,1000000\n",
        encoding="utf-8-sig",
    )

    repo = PEV24CafeFRepository(
        paths=PEV24Paths(cafef_all_csv_path=str(file_path)),
    )

    rows = repo.load_rows()

    assert rows[0].symbol == "FPT"
    assert rows[0].close == 100