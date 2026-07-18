from infrastructure.pe_v24.client_repository import PEV24ClientRepository


def test_pe_v24_client_repository_load_clients(tmp_path):
    file_path = tmp_path / "clients.csv"

    file_path.write_text(
        "client_id,name,cash\n"
        "anh_dung,Anh Dung,25000000\n"
        "chi_lan,Chi Lan,15000000\n",
        encoding="utf-8-sig",
    )

    repo = PEV24ClientRepository(csv_path=str(file_path))

    clients = repo.load_clients()

    assert len(clients) == 2
    assert clients[0].client_id == "anh_dung"
    assert clients[0].name == "Anh Dung"
    assert clients[0].cash == 25000000


def test_pe_v24_client_repository_load_client_ids(tmp_path):
    file_path = tmp_path / "clients.csv"

    file_path.write_text(
        "client_id,name,cash\n"
        "anh_dung,Anh Dung,25000000\n"
        "chi_lan,Chi Lan,15000000\n",
        encoding="utf-8-sig",
    )

    repo = PEV24ClientRepository(csv_path=str(file_path))

    assert repo.load_client_ids() == ["anh_dung", "chi_lan"]


def test_pe_v24_client_repository_rejects_empty_path():
    try:
        PEV24ClientRepository(csv_path="")
    except ValueError as exc:
        assert str(exc) == "csv_path must not be empty"
    else:
        assert False