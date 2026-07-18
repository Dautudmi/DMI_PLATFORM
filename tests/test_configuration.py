from infrastructure.configuration import (
    Configuration,
    EnvironmentConfigurationLoader,
)


def test_get():
    config = Configuration({"A": "1"})

    assert config.get("A") == "1"


def test_default():
    config = Configuration({})

    assert config.get("ABC", "x") == "x"


def test_require():
    config = Configuration({"A": "123"})

    assert config.require("A") == "123"


def test_require_raise():
    config = Configuration({})

    try:
        config.require("ABC")
    except ValueError:
        assert True
    else:
        assert False


def test_env_loader(monkeypatch):
    monkeypatch.setenv("TOKEN", "abc")

    loader = EnvironmentConfigurationLoader()

    config = loader.load(["TOKEN"])

    assert config.require("TOKEN") == "abc"