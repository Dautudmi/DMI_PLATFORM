from infrastructure.logger import SimpleLogger


def test_info(capsys):
    logger = SimpleLogger()

    logger.info("hello")

    out = capsys.readouterr().out

    assert "[INFO]" in out
    assert "hello" in out


def test_warning(capsys):
    logger = SimpleLogger()

    logger.warning("warning")

    out = capsys.readouterr().out

    assert "[WARNING]" in out


def test_error(capsys):
    logger = SimpleLogger()

    logger.error("error")

    out = capsys.readouterr().out

    assert "[ERROR]" in out