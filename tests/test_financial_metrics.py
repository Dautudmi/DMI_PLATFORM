from dmi_core.metrics import FinancialMetrics
from dmi_core.services import FinancialStatementService


def test_financial_metrics():

    service = FinancialStatementService()

    statement = service.get(
        symbol="AAA",
        period="QUY",
        page_size=4,
    )

    metrics = FinancialMetrics(statement)

    roe = metrics.roe()
    roa = metrics.roa()
    gross_margin = metrics.gross_margin()
    net_margin = metrics.net_margin()
    current_ratio = metrics.current_ratio()
    debt_to_equity = metrics.debt_to_equity()
    debt_to_assets = metrics.debt_to_assets()
    asset_turnover = metrics.asset_turnover()
    eps = metrics.eps()
    bvps = metrics.bvps()

    assert roe.code == "ROE"
    assert roe.value is not None
    assert roe.display.endswith("%")

    assert roa.code == "ROA"
    assert gross_margin.code == "GROSS_MARGIN"
    assert net_margin.code == "NET_MARGIN"
    assert current_ratio.code == "CURRENT_RATIO"
    assert debt_to_equity.code == "DEBT_TO_EQUITY"
    assert debt_to_assets.code == "DEBT_TO_ASSETS"
    assert asset_turnover.code == "ASSET_TURNOVER"
    assert eps.code == "EPS"
    assert bvps.code == "BVPS"

    all_metrics = metrics.all()

    assert len(all_metrics) == 10
    assert all_metrics[0].code == "ROE"

    print("=" * 60)
    print("DMI FINANCIAL METRICS")
    print("=" * 60)

    print("ROE           :", roe.display)
    print("ROA           :", roa.display)
    print("Gross Margin  :", gross_margin.display)
    print("Net Margin    :", net_margin.display)
    print("Current Ratio :", current_ratio.display)
    print("Debt / Equity :", debt_to_equity.display)
    print("Debt / Assets :", debt_to_assets.display)
    print("Asset Turnover:", asset_turnover.display)
    print("EPS           :", eps.display)
    print("BVPS          :", bvps.display)

    print("-" * 60)
    print("ALL METRICS")

    for metric in all_metrics:
        print(
            metric.code,
            "|",
            metric.name,
            "|",
            metric.display,
            "|",
            metric.unit,
        )

    print("=" * 60)


if __name__ == "__main__":
    test_financial_metrics()