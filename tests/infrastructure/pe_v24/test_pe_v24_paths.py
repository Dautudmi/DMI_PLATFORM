from infrastructure.pe_v24.pe_v24_paths import PEV24Paths


def test_pe_v24_paths_require_cafef_path():
    paths = PEV24Paths(cafef_all_csv_path="F:/DATA/CafeF/CafeF_ALL.csv")

    assert paths.require_cafef_all_csv_path() == "F:/DATA/CafeF/CafeF_ALL.csv"


def test_pe_v24_paths_reject_empty_cafef_path():
    paths = PEV24Paths(cafef_all_csv_path="")

    try:
        paths.require_cafef_all_csv_path()
    except ValueError as exc:
        assert str(exc) == "cafef_all_csv_path must not be empty"
    else:
        assert False