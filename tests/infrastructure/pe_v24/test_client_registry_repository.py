from infrastructure.pe_v24.client_registry_repository import (
    PEV24ClientRegistryRepository,
)


def test_client_registry_repository_loads_real_pe_structure(
    tmp_path,
):
    file_path = tmp_path / "client_config.csv"

    file_path.write_text(
        "Client,Capital,CashPercent\n"
        "anh_dung,1000000000,0\n"
        "anh_manh,300000000,0\n",
        encoding="utf-8-sig",
    )

    repository = PEV24ClientRegistryRepository(
        csv_path=str(file_path)
    )

    clients = repository.load_clients()

    assert len(clients) == 2

    assert clients[0].client_id == "anh_dung"
    assert clients[0].capital == 1000000000
    assert clients[0].cash_percent == 0

    assert clients[1].client_id == "anh_manh"
    assert clients[1].capital == 300000000


def test_client_registry_repository_load_client_ids(tmp_path):
    file_path = tmp_path / "client_config.csv"

    file_path.write_text(
        "Client,Capital,CashPercent\n"
        "anh_dung,1000000000,0\n"
        "anh_manh,300000000,0\n",
        encoding="utf-8-sig",
    )

    repository = PEV24ClientRegistryRepository(
        csv_path=str(file_path)
    )

    assert repository.load_client_ids() == [
        "anh_dung",
        "anh_manh",
    ]


def test_client_registry_repository_find_by_id(tmp_path):
    file_path = tmp_path / "client_config.csv"

    file_path.write_text(
        "Client,Capital,CashPercent\n"
        "anh_manh,300000000,0.25\n",
        encoding="utf-8-sig",
    )

    repository = PEV24ClientRegistryRepository(
        csv_path=str(file_path)
    )

    client = repository.find_by_id("anh_manh")

    assert client is not None
    assert client.client_id == "anh_manh"
    assert client.capital == 300000000
    assert client.cash_percent == 0.25


def test_client_registry_repository_require_missing_client(
    tmp_path,
):
    file_path = tmp_path / "client_config.csv"

    file_path.write_text(
        "Client,Capital,CashPercent\n"
        "anh_manh,300000000,0\n",
        encoding="utf-8-sig",
    )

    repository = PEV24ClientRegistryRepository(
        csv_path=str(file_path)
    )

    try:
        repository.require_by_id("khong_ton_tai")
    except KeyError as exc:
        assert "Client not found: khong_ton_tai" in str(exc)
    else:
        assert False