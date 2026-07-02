# DMI Financial Dictionary

> Standard financial metrics dictionary for DMI Platform

Version: 1.0  
Status: Draft  
Scope: Financial Metrics, Analysis, Valuation, Screening

---

# Purpose

The Financial Dictionary defines the standard language of DMI Platform.

It is used by:

- Financial Metrics
- Financial Analysis
- Valuation Engine
- Screening Engine
- Portfolio Engine
- AI Investment Assistant
- Dashboard
- Reports

---

# Metric Categories

## 1. Profitability

| Code | Name | Unit | Formula | Description |
|---|---|---|---|---|
| ROE | Return on Equity | % | Net Profit / Equity | Measures profitability relative to shareholder equity |
| ROA | Return on Assets | % | Net Profit / Total Assets | Measures profitability relative to assets |
| GROSS_MARGIN | Gross Margin | % | Gross Profit / Revenue | Measures gross profitability |
| NET_MARGIN | Net Margin | % | Net Profit / Revenue | Measures net profitability |
| OPERATING_MARGIN | Operating Margin | % | Operating Profit / Revenue | Measures operating profitability |
| ROIC | Return on Invested Capital | % | NOPAT / Invested Capital | Measures return on invested capital |

---

## 2. Liquidity

| Code | Name | Unit | Formula | Description |
|---|---|---|---|---|
| CURRENT_RATIO | Current Ratio | x | Current Assets / Current Liabilities | Measures short-term liquidity |
| QUICK_RATIO | Quick Ratio | x | (Current Assets - Inventory) / Current Liabilities | Measures liquidity excluding inventory |
| CASH_RATIO | Cash Ratio | x | Cash / Current Liabilities | Measures immediate liquidity |

---

## 3. Leverage

| Code | Name | Unit | Formula | Description |
|---|---|---|---|---|
| DEBT_TO_EQUITY | Debt to Equity | x | Total Debt / Equity | Measures leverage relative to equity |
| DEBT_TO_ASSETS | Debt to Assets | % | Total Debt / Total Assets | Measures debt level relative to assets |
| INTEREST_COVERAGE | Interest Coverage | x | EBIT / Interest Expense | Measures ability to pay interest expense |

---

## 4. Efficiency

| Code | Name | Unit | Formula | Description |
|---|---|---|---|---|
| ASSET_TURNOVER | Asset Turnover | x | Revenue / Total Assets | Measures asset efficiency |
| INVENTORY_TURNOVER | Inventory Turnover | x | Cost of Goods Sold / Inventory | Measures inventory efficiency |
| RECEIVABLE_TURNOVER | Receivable Turnover | x | Revenue / Receivables | Measures receivable collection efficiency |

---

## 5. Per Share

| Code | Name | Unit | Formula | Description |
|---|---|---|---|---|
| EPS | Earnings Per Share | VND/share | Net Profit / Shares Outstanding | Measures profit per share |
| BVPS | Book Value Per Share | VND/share | Equity / Shares Outstanding | Measures book value per share |

---

## 6. Growth

| Code | Name | Unit | Formula | Description |
|---|---|---|---|---|
| REVENUE_GROWTH | Revenue Growth | % | Revenue This Period / Revenue Previous Period - 1 | Measures revenue growth |
| NET_PROFIT_GROWTH | Net Profit Growth | % | Net Profit This Period / Net Profit Previous Period - 1 | Measures earnings growth |
| EPS_GROWTH | EPS Growth | % | EPS This Period / EPS Previous Period - 1 | Measures EPS growth |

---

## 7. Cash Flow

| Code | Name | Unit | Formula | Description |
|---|---|---|---|---|
| OCF | Operating Cash Flow | VND | Cash Flow From Operations | Measures operating cash generation |
| FCF | Free Cash Flow | VND | Operating Cash Flow - CAPEX | Measures free cash flow |
| FCF_MARGIN | Free Cash Flow Margin | % | Free Cash Flow / Revenue | Measures free cash flow efficiency |

---

## 8. Valuation

| Code | Name | Unit | Formula | Description |
|---|---|---|---|---|
| PE | Price to Earnings | x | Market Price / EPS | Measures price relative to earnings |
| PB | Price to Book | x | Market Price / BVPS | Measures price relative to book value |
| PS | Price to Sales | x | Market Capitalization / Revenue | Measures price relative to sales |
| EV_EBITDA | EV/EBITDA | x | Enterprise Value / EBITDA | Measures enterprise value relative to EBITDA |
| PEG | Price Earnings Growth | x | PE / EPS Growth | Measures valuation adjusted for growth |

---

# Data Dependencies

## Balance Sheet

Required fields:

- cash
- receivables
- inventory
- current_assets
- current_liabilities
- total_debt
- total_assets
- equity
- shares_outstanding

## Income Statement

Required fields:

- revenue
- cost_of_goods_sold
- gross_profit
- operating_profit
- ebit
- interest_expense
- net_profit

## Cash Flow Statement

Required fields:

- operating_cash_flow
- capex
- free_cash_flow

## Market Data

Required fields:

- current_price
- market_cap
- enterprise_value

---

# Design Rules

## Rule 1: Metrics must not call Provider

Metrics only receive standardized DMI Domain Models.

## Rule 2: Metrics must return MetricResult

All metric calculations must return:

```python
MetricResult