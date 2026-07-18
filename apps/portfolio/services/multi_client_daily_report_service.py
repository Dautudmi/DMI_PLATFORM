from pathlib import Path

from apps.portfolio.services.daily_portfolio_report_service import (
    DailyPortfolioReportService,
)


class MultiClientDailyReportService:
    """
    Generate daily portfolio reports for all client CSV files in a folder.
    """

    def __init__(self) -> None:
        self._daily_report_service = DailyPortfolioReportService()

    def generate_all(
        self,
        folder: str | Path,
    ) -> dict[str, str]:
        folder = Path(folder)

        reports: dict[str, str] = {}

        for csv_file in sorted(folder.glob("*.csv")):
            reports[csv_file.name] = self._daily_report_service.generate(
                csv_file
            )

        return reports