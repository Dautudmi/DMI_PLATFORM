from pathlib import Path

from apps.portfolio.loaders import ClientPortfolioLoader
from apps.portfolio.use_cases import DailyPortfolioReportUseCase
from presentation.telegram import TelegramRenderer


class DailyPortfolioReportService:
    """
    High-level facade for generating daily portfolio report text.

    Input:
        client CSV file

    Output:
        Telegram-ready text
    """

    def __init__(self) -> None:
        self._loader = ClientPortfolioLoader()
        self._use_case = DailyPortfolioReportUseCase()
        self._renderer = TelegramRenderer()

    def generate(
        self,
        csv_file: str | Path,
    ) -> str:
        portfolio = self._loader.load(csv_file)

        report = self._use_case.execute(portfolio)

        return self._renderer.render(report)