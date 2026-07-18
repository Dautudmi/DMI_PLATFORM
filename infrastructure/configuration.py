from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


class ConfigurationError(ValueError):
    """
    Raised when application configuration is missing
    or invalid.
    """


@dataclass(frozen=True, slots=True)
class Configuration:
    """
    Immutable application configuration.

    Values are stored as strings because environment
    variables are string-based.

    Typed accessors are provided for:
    - required text
    - optional text
    - bool
    - int
    - float
    - path
    """

    values: Mapping[str, str]

    def get(
        self,
        key: str,
        default: str | None = None,
    ) -> str | None:
        normalized_key = self._normalize_key(key)

        value = self.values.get(
            normalized_key,
            default,
        )

        if value is None:
            return None

        return str(value)

    def require(
        self,
        key: str,
    ) -> str:
        normalized_key = self._normalize_key(key)

        value = self.get(normalized_key)

        if value is None or not value.strip():
            raise ConfigurationError(
                f"Missing required config: "
                f"{normalized_key}"
            )

        return value.strip()

    def get_text(
        self,
        key: str,
        default: str | None = None,
    ) -> str | None:
        value = self.get(
            key=key,
            default=default,
        )

        if value is None:
            return None

        normalized_value = str(value).strip()

        return normalized_value or None

    def get_bool(
        self,
        key: str,
        default: bool = False,
    ) -> bool:
        value = self.get_text(key)

        if value is None:
            return bool(default)

        normalized_value = value.lower()

        truthy_values = {
            "1",
            "true",
            "yes",
            "y",
            "on",
            "enabled",
        }

        falsy_values = {
            "0",
            "false",
            "no",
            "n",
            "off",
            "disabled",
        }

        if normalized_value in truthy_values:
            return True

        if normalized_value in falsy_values:
            return False

        raise ConfigurationError(
            f"Invalid boolean config "
            f"{self._normalize_key(key)}: {value}"
        )

    def get_int(
        self,
        key: str,
        default: int | None = None,
    ) -> int | None:
        value = self.get_text(key)

        if value is None:
            return default

        try:
            return int(value)

        except ValueError as exc:
            raise ConfigurationError(
                f"Invalid integer config "
                f"{self._normalize_key(key)}: {value}"
            ) from exc

    def get_float(
        self,
        key: str,
        default: float | None = None,
    ) -> float | None:
        value = self.get_text(key)

        if value is None:
            return default

        try:
            return float(value)

        except ValueError as exc:
            raise ConfigurationError(
                f"Invalid float config "
                f"{self._normalize_key(key)}: {value}"
            ) from exc

    def get_path(
        self,
        key: str,
        default: str | Path | None = None,
    ) -> Path | None:
        value = self.get_text(key)

        if value is None:
            if default is None:
                return None

            return Path(default)

        return Path(value)

    def require_path(
        self,
        key: str,
    ) -> Path:
        value = self.require(key)

        return Path(value)

    def require_existing_file(
        self,
        key: str,
    ) -> Path:
        path = self.require_path(key)

        if not path.is_file():
            raise ConfigurationError(
                f"Configured file does not exist "
                f"for {self._normalize_key(key)}: "
                f"{path}"
            )

        return path

    def require_existing_directory(
        self,
        key: str,
    ) -> Path:
        path = self.require_path(key)

        if not path.is_dir():
            raise ConfigurationError(
                f"Configured directory does not exist "
                f"for {self._normalize_key(key)}: "
                f"{path}"
            )

        return path

    def contains(
        self,
        key: str,
    ) -> bool:
        normalized_key = self._normalize_key(key)

        value = self.values.get(normalized_key)

        return (
            value is not None
            and bool(str(value).strip())
        )

    def _normalize_key(
        self,
        key: str,
    ) -> str:
        if key is None or not str(key).strip():
            raise ValueError(
                "configuration key must not be empty"
            )

        return str(key).strip()


class EnvironmentConfigurationLoader:
    """
    Load Configuration from environment variables.

    Responsibility:
    - read environment variables
    - optionally restrict loaded keys
    - return immutable Configuration

    Không:
    - validate business paths
    - build repositories
    - build ApplicationContainer
    """

    def __init__(
        self,
        environment: Mapping[str, str] | None = None,
    ) -> None:
        self._environment = (
            environment
            if environment is not None
            else os.environ
        )

    def load(
        self,
        keys: list[str] | tuple[str, ...] | None = None,
    ) -> Configuration:
        if keys is None:
            return Configuration(
                values=dict(self._environment)
            )

        values: dict[str, str] = {}

        for key in keys:
            normalized_key = self._normalize_key(key)

            if normalized_key in self._environment:
                values[normalized_key] = str(
                    self._environment[
                        normalized_key
                    ]
                )

        return Configuration(values=values)

    def _normalize_key(
        self,
        key: str,
    ) -> str:
        if key is None or not str(key).strip():
            raise ValueError(
                "configuration key must not be empty"
            )

        return str(key).strip()


class ConfigurationProvider:
    """
    High-level typed configuration provider.

    Application code may depend on this provider instead
    of reading os.environ directly.

    It wraps Configuration and exposes typed accessors.
    """

    def __init__(
        self,
        configuration: Configuration,
    ) -> None:
        if configuration is None:
            raise ValueError(
                "configuration must not be None"
            )

        self._configuration = configuration

    @property
    def configuration(self) -> Configuration:
        return self._configuration

    def get(
        self,
        key: str,
        default: str | None = None,
    ) -> str | None:
        return self._configuration.get(
            key=key,
            default=default,
        )

    def require(
        self,
        key: str,
    ) -> str:
        return self._configuration.require(key)

    def get_bool(
        self,
        key: str,
        default: bool = False,
    ) -> bool:
        return self._configuration.get_bool(
            key=key,
            default=default,
        )

    def get_int(
        self,
        key: str,
        default: int | None = None,
    ) -> int | None:
        return self._configuration.get_int(
            key=key,
            default=default,
        )

    def get_float(
        self,
        key: str,
        default: float | None = None,
    ) -> float | None:
        return self._configuration.get_float(
            key=key,
            default=default,
        )

    def get_path(
        self,
        key: str,
        default: str | Path | None = None,
    ) -> Path | None:
        return self._configuration.get_path(
            key=key,
            default=default,
        )

    def require_path(
        self,
        key: str,
    ) -> Path:
        return self._configuration.require_path(key)

    def require_existing_file(
        self,
        key: str,
    ) -> Path:
        return (
            self._configuration
            .require_existing_file(key)
        )

    def require_existing_directory(
        self,
        key: str,
    ) -> Path:
        return (
            self._configuration
            .require_existing_directory(key)
        )