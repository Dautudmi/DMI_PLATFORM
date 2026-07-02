"""
DMI Platform

Metric Catalog

Single Source of Truth for all financial metrics.
"""

from dmi_core.models.metric_definition import MetricDefinition

# ==========================================================
# PROFITABILITY
# ==========================================================

ROE = MetricDefinition(
    code="ROE",
    name="Return on Equity",
    category="Profitability",
    unit="%",
    formula="Net Profit / Equity",
    description="Measures profitability relative to shareholder equity."
)

ROA = MetricDefinition(
    code="ROA",
    name="Return on Assets",
    category="Profitability",
    unit="%",
    formula="Net Profit / Total Assets",
    description="Measures profitability relative to total assets."
)

GROSS_MARGIN = MetricDefinition(
    code="GROSS_MARGIN",
    name="Gross Margin",
    category="Profitability",
    unit="%",
    formula="Gross Profit / Revenue",
    description="Measures gross profitability."
)

NET_MARGIN = MetricDefinition(
    code="NET_MARGIN",
    name="Net Margin",
    category="Profitability",
    unit="%",
    formula="Net Profit / Revenue",
    description="Measures net profitability."
)

# ==========================================================
# LEVERAGE
# ==========================================================

DEBT_TO_EQUITY = MetricDefinition(
    code="DEBT_TO_EQUITY",
    name="Debt to Equity",
    category="Leverage",
    unit="x",
    formula="Total Debt / Equity",
    description="Measures financial leverage."
)

DEBT_TO_ASSETS = MetricDefinition(
    code="DEBT_TO_ASSETS",
    name="Debt to Assets",
    category="Leverage",
    unit="%",
    formula="Total Debt / Total Assets",
    description="Measures debt relative to total assets."
)

# ==========================================================
# LIQUIDITY
# ==========================================================

CURRENT_RATIO = MetricDefinition(
    code="CURRENT_RATIO",
    name="Current Ratio",
    category="Liquidity",
    unit="x",
    formula="Current Assets / Current Liabilities",
    description="Measures short-term liquidity."
)

# ==========================================================
# EFFICIENCY
# ==========================================================

ASSET_TURNOVER = MetricDefinition(
    code="ASSET_TURNOVER",
    name="Asset Turnover",
    category="Efficiency",
    unit="x",
    formula="Revenue / Total Assets",
    description="Measures asset efficiency."
)

# ==========================================================
# PER SHARE
# ==========================================================

EPS = MetricDefinition(
    code="EPS",
    name="Earnings Per Share",
    category="Per Share",
    unit="VND/share",
    formula="Net Profit / Shares Outstanding",
    description="Measures earnings per share."
)

BVPS = MetricDefinition(
    code="BVPS",
    name="Book Value Per Share",
    category="Per Share",
    unit="VND/share",
    formula="Equity / Shares Outstanding",
    description="Measures book value per share."
)

# ==========================================================
# ALL METRICS
# ==========================================================

ALL_METRICS = [
    ROE,
    ROA,
    GROSS_MARGIN,
    NET_MARGIN,
    DEBT_TO_EQUITY,
    DEBT_TO_ASSETS,
    CURRENT_RATIO,
    ASSET_TURNOVER,
    EPS,
    BVPS,
]