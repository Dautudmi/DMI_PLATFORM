from pathlib import Path

from apps.portfolio.services import DailyPortfolioReportService


def test_daily_portfolio_report_service_generates_telegram_text(
    tmp_path: Path,
):
    csv = tmp_path / "client.csv"

    csv.write_text(
        """Client Name,Demo
Cash,10000000

Symbol,Quantity,Average Cost,Current Price
FPT,100,90000,100000
MBB,200,25000,27000
""",
        encoding="utf-8",
    )

    text = DailyPortfolioReportService().generate(csv)

    assert "DMI DAILY PORTFOLIO REPORT" in text
    assert "Demo" in text
    assert "Health" in text