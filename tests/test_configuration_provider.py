from __future__ import annotations

from pathlib import Path

import pytest

from infrastructure.configuration import (
    Configuration,
    ConfigurationError,
    ConfigurationProvider,
    EnvironmentConfigurationLoader,
)


def test_configuration_get_returns_value() -> None:
    configuration = Configuration(
        values={
            "DMI_TEST_KEY": "value"
        }
    )

    assert (
        configuration.get("DMI_TEST_KEY")
        == "value"
    )


def test_configuration_get_returns_default() -> None:
    configuration = Configuration(values={})

    assert (
        configuration.get(
            "DMI_TEST_KEY",
            "default",
        )
        == "default"
    )


def test_require_returns_trimmed_value() -> None:
    configuration = Configuration(
        values={
            "DMI_TEST_KEY": "  value  "
        }
    )

    assert (
        configuration.require(
            "DMI_TEST_KEY"
        )
        == "value"
    )


def test_require_rejects_missing_value() -> None:
    configuration = Configuration(values={})

    with pytest.raises(
        ConfigurationError,
        match=(
            "Missing required config: "
            "DMI_TEST_KEY"
        ),
    ):
        configuration.require(
            "DMI_TEST_KEY"
        )


@pytest.mark.parametrize(
    "value",
    [
        "1",
        "true",
        "TRUE",
        "yes",
        "on",
        "enabled",
    ],
)
def test_get_bool_returns_true(
    value: str,
) -> None:
    configuration = Configuration(
        values={
            "DMI_FLAG": value
        }
    )

    assert (
        configuration.get_bool(
            "DMI_FLAG"
        )
        is True
    )


@pytest.mark.parametrize(
    "value",
    [
        "0",
        "false",
        "FALSE",
        "no",
        "off",
        "disabled",
    ],
)
def test_get_bool_returns_false(
    value: str,
) -> None:
    configuration = Configuration(
        values={
            "DMI_FLAG": value
        }
    )

    assert (
        configuration.get_bool(
            "DMI_FLAG"
        )
        is False
    )


def test_get_bool_uses_default() -> None:
    configuration = Configuration(values={})

    assert (
        configuration.get_bool(
            "DMI_FLAG",
            default=True,
        )
        is True
    )


def test_get_bool_rejects_invalid_value() -> None:
    configuration = Configuration(
        values={
            "DMI_FLAG": "maybe"
        }
    )

    with pytest.raises(
        ConfigurationError,
        match=(
            "Invalid boolean config "
            "DMI_FLAG"
        ),
    ):
        configuration.get_bool(
            "DMI_FLAG"
        )


def test_get_int_returns_integer() -> None:
    configuration = Configuration(
        values={
            "DMI_MAX_CLIENTS": "100"
        }
    )

    assert (
        configuration.get_int(
            "DMI_MAX_CLIENTS"
        )
        == 100
    )


def test_get_int_uses_default() -> None:
    configuration = Configuration(values={})

    assert (
        configuration.get_int(
            "DMI_MAX_CLIENTS",
            default=50,
        )
        == 50
    )


def test_get_int_rejects_invalid_value() -> None:
    configuration = Configuration(
        values={
            "DMI_MAX_CLIENTS": "abc"
        }
    )

    with pytest.raises(
        ConfigurationError,
        match=(
            "Invalid integer config "
            "DMI_MAX_CLIENTS"
        ),
    ):
        configuration.get_int(
            "DMI_MAX_CLIENTS"
        )


def test_get_float_returns_float() -> None:
    configuration = Configuration(
        values={
            "DMI_THRESHOLD": "0.25"
        }
    )

    assert (
        configuration.get_float(
            "DMI_THRESHOLD"
        )
        == 0.25
    )


def test_get_path_returns_path() -> None:
    configuration = Configuration(
        values={
            "DMI_PATH": (
                r"F:\DATA\Portfolio"
            )
        }
    )

    assert configuration.get_path(
        "DMI_PATH"
    ) == Path(
        r"F:\DATA\Portfolio"
    )


def test_require_existing_file(
    tmp_path: Path,
) -> None:
    file_path = (
        tmp_path / "client_config.csv"
    )

    file_path.write_text(
        "Client,Capital,CashPercent\n",
        encoding="utf-8",
    )

    configuration = Configuration(
        values={
            "DMI_FILE": str(file_path)
        }
    )

    assert (
        configuration.require_existing_file(
            "DMI_FILE"
        )
        == file_path
    )


def test_require_existing_file_rejects_missing_file(
    tmp_path: Path,
) -> None:
    file_path = (
        tmp_path / "missing.csv"
    )

    configuration = Configuration(
        values={
            "DMI_FILE": str(file_path)
        }
    )

    with pytest.raises(
        ConfigurationError,
        match=(
            "Configured file does not exist"
        ),
    ):
        configuration.require_existing_file(
            "DMI_FILE"
        )


def test_require_existing_directory(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "clients"

    folder.mkdir()

    configuration = Configuration(
        values={
            "DMI_FOLDER": str(folder)
        }
    )

    assert (
        configuration
        .require_existing_directory(
            "DMI_FOLDER"
        )
        == folder
    )


def test_require_existing_directory_rejects_missing_folder(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "missing"

    configuration = Configuration(
        values={
            "DMI_FOLDER": str(folder)
        }
    )

    with pytest.raises(
        ConfigurationError,
        match=(
            "Configured directory "
            "does not exist"
        ),
    ):
        configuration.require_existing_directory(
            "DMI_FOLDER"
        )


def test_environment_loader_loads_selected_keys() -> None:
    loader = EnvironmentConfigurationLoader(
        environment={
            "DMI_ONE": "1",
            "DMI_TWO": "2",
            "OTHER": "ignored",
        }
    )

    configuration = loader.load(
        keys=[
            "DMI_ONE",
            "DMI_TWO",
        ]
    )

    assert configuration.values == {
        "DMI_ONE": "1",
        "DMI_TWO": "2",
    }


def test_environment_loader_loads_all_keys() -> None:
    loader = EnvironmentConfigurationLoader(
        environment={
            "DMI_ONE": "1",
            "DMI_TWO": "2",
        }
    )

    configuration = loader.load()

    assert configuration.values == {
        "DMI_ONE": "1",
        "DMI_TWO": "2",
    }


def test_configuration_provider_delegates_access() -> None:
    configuration = Configuration(
        values={
            "DMI_FLAG": "true",
            "DMI_COUNT": "20",
        }
    )

    provider = ConfigurationProvider(
        configuration=configuration
    )

    assert (
        provider.configuration
        is configuration
    )

    assert provider.get_bool(
        "DMI_FLAG"
    ) is True

    assert provider.get_int(
        "DMI_COUNT"
    ) == 20


def test_configuration_provider_rejects_none() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "configuration must not be None"
        ),
    ):
        ConfigurationProvider(
            configuration=None
        )


def test_rejects_empty_configuration_key() -> None:
    configuration = Configuration(values={})

    with pytest.raises(
        ValueError,
        match=(
            "configuration key "
            "must not be empty"
        ),
    ):
        configuration.get("   ")