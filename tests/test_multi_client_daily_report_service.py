from pathlib import Path

from apps.portfolio.services import MultiClientDailyReportService


def test_multi_client_daily_report_service_generates_reports(
    tmp_path: Path,
):
    client_a = tmp_path / "client_a.csv"
    client_b = tmp_path / "client_b.csv"

    client_a.write_text(
        """Client Name,Client A
Cash,10000000

Symbol,Quantity,Average Cost,Current Price
FPT,100,90000,100000
""",
        encoding="utf-8",
    )

    client_b.write_text(
        """Client Name,Client B
Cash,15000000

Symbol,Quantity,Average Cost,Current Price
MBB,200,25000,27000
""",
        encoding="utf-8",
    )

    reports = MultiClientDailyReportService().generate_all(tmp_path)

    assert len(reports) == 2
    assert "client_a.csv" in reports
    assert "client_b.csv" in reports
    assert "Client A" in reports["client_a.csv"]
    assert "Client B" in reports["client_b.csv"]