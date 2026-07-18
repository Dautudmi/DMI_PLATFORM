from infrastructure.file_storage import FileStorage


def test_write_and_read_text(tmp_path):
    storage = FileStorage()

    file_path = tmp_path / "test.txt"

    storage.write_text(str(file_path), "hello")

    assert storage.exists(str(file_path))
    assert storage.is_file(str(file_path))
    assert storage.read_text(str(file_path)) == "hello"


def test_ensure_dir(tmp_path):
    storage = FileStorage()

    folder = tmp_path / "reports"

    storage.ensure_dir(str(folder))

    assert storage.exists(str(folder))
    assert storage.is_dir(str(folder))