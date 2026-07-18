from __future__ import annotations

from typing import Any

from apps.portfolio.providers.financial_data_provider import (
    FinancialDataProvider,
)
from apps.shared.containers.application import (
    ApplicationContainer,
)
from infrastructure.configuration import (
    Configuration,
    ConfigurationProvider,
    EnvironmentConfigurationLoader,
)
from infrastructure.pe_v24.client_portfolio_repository import (
    PEV24ClientPortfolioRepository,
)
from infrastructure.pe_v24.client_registry_repository import (
    PEV24ClientRegistryRepository,
)


PEV24_CLIENT_CONFIG_PATH_KEY = (
    "DMI_PEV24_CLIENT_CONFIG_PATH"
)

PEV24_CLIENTS_FOLDER_PATH_KEY = (
    "DMI_PEV24_CLIENTS_FOLDER_PATH"
)


PRODUCTION_CONFIGURATION_KEYS = (
    PEV24_CLIENT_CONFIG_PATH_KEY,
    PEV24_CLIENTS_FOLDER_PATH_KEY,
)


def build_application(
    configuration: Configuration | None = None,
    configuration_provider: (
        ConfigurationProvider | None
    ) = None,
    financial_provider: FinancialDataProvider | None = None,
    daily_portfolio_report_service: Any | None = None,
) -> ApplicationContainer:
    """
    Build the DMI production ApplicationContainer.

    Configuration keys:

    DMI_PEV24_CLIENT_CONFIG_PATH
        Path to client_config.csv.

    DMI_PEV24_CLIENTS_FOLDER_PATH
        Folder containing client_<client_id>.csv files.

    Responsibility:
    - resolve ConfigurationProvider
    - validate production paths
    - create PE_V2.4 repositories
    - inject repositories into ApplicationContainer

    Không:
    - chạy DailyProductionRunner
    - gửi Telegram
    - chạy Scheduler
    - chứa business logic
    """

    provider = _resolve_configuration_provider(
        configuration=configuration,
        configuration_provider=(
            configuration_provider
        ),
    )

    client_config_path = (
        provider.require_existing_file(
            PEV24_CLIENT_CONFIG_PATH_KEY
        )
    )

    clients_folder_path = (
        provider.require_existing_directory(
            PEV24_CLIENTS_FOLDER_PATH_KEY
        )
    )

    client_registry_repository = (
        PEV24ClientRegistryRepository(
            csv_path=str(client_config_path),
        )
    )

    client_portfolio_repository = (
        PEV24ClientPortfolioRepository(
            clients_folder_path=str(
                clients_folder_path
            ),
        )
    )

    return ApplicationContainer(
        financial_provider=financial_provider,
        client_registry_repository=(
            client_registry_repository
        ),
        client_portfolio_repository=(
            client_portfolio_repository
        ),
        daily_portfolio_report_service=(
            daily_portfolio_report_service
        ),
    )


def load_production_configuration(
) -> Configuration:
    """
    Load production configuration from environment.
    """

    loader = EnvironmentConfigurationLoader()

    return loader.load(
        keys=list(PRODUCTION_CONFIGURATION_KEYS)
    )


def build_configuration_provider(
    configuration: Configuration | None = None,
) -> ConfigurationProvider:
    """
    Build ConfigurationProvider from an injected
    Configuration or from production environment.
    """

    resolved_configuration = (
        configuration
        if configuration is not None
        else load_production_configuration()
    )

    return ConfigurationProvider(
        configuration=resolved_configuration
    )


def _resolve_configuration_provider(
    configuration: Configuration | None,
    configuration_provider: (
        ConfigurationProvider | None
    ),
) -> ConfigurationProvider:
    if (
        configuration is not None
        and configuration_provider is not None
    ):
        raise ValueError(
            "provide either configuration or "
            "configuration_provider, not both"
        )

    if configuration_provider is not None:
        return configuration_provider

    return build_configuration_provider(
        configuration=configuration
    )