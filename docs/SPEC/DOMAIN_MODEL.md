# DMI Platform Domain Model

Version: 1.0

Status: Official

---

# 1. Purpose

This document defines every core Domain Object used within the DMI Platform.

Every module must communicate using these Domain Models.

Raw dictionaries are not allowed.

---

# 2. Domain Architecture

```
Financial Data

↓

Financial Statement

↓

Financial Metrics

↓

Financial Analysis

↓

Valuation

↓

Decision

↓

Applications

↓

AI
```

---

# 3. Domain Objects

## FinancialStatement

Purpose

Represents standardized financial statements.

Contains

- Balance Sheet
- Income Statement

Responsibility

Store raw financial data only.

Must NOT

Calculate metrics.

---

## BalanceSheet

Purpose

Store balance sheet data.

Examples

Cash

Inventory

Receivables

Current Assets

Current Liabilities

Total Assets

Total Debt

Equity

Shares Outstanding

---

## IncomeStatement

Purpose

Store income statement data.

Examples

Revenue

Gross Profit

Operating Profit

EBIT

Interest Expense

Net Profit

---

## MetricResult

Purpose

Represents one calculated financial metric.

Example

ROE

ROA

EPS

BVPS

Contains

Metric Code

Metric Name

Value

Display Value

Description

---

## FinancialMetrics

Purpose

Calculate all financial metrics.

Responsibilities

Read FinancialStatement.

Calculate metrics.

Return MetricResult.

Must NOT

Contain business rules.

---

## AnalysisResult

Purpose

Represents evaluation of one financial aspect.

Examples

Profitability

Leverage

Liquidity

Growth

Contains

Rating

Score

Summary

Recommendation

---

## FinancialAnalysisResult

Purpose

Aggregate all Analysis Results.

Contains

Profitability

Leverage

Liquidity

Efficiency

Growth

Overall Score

Overall Rating

Recommendation

---

## ValuationConfig

Purpose

Store valuation assumptions.

Examples

Target PE

Target PB

Discount Rate

Margin of Safety

---

## ValuationResult

Purpose

Represent one valuation result.

Contains

Method

Intrinsic Value

Current Price

Upside

Downside

Margin of Safety

Recommendation

---

## DecisionResult

Purpose

Represent final investment decision.

Status

Planned

Future Fields

Decision

Confidence

Reason

Risk

Target Price

Stop Loss

---

# 4. Layer Communication

```
Provider

↓

Parser

↓

Mapper

↓

FinancialStatement

↓

FinancialMetrics

↓

FinancialAnalysis

↓

Valuation

↓

Decision

↓

Applications
```

Every layer communicates only with adjacent layers.

---

# 5. Layer Responsibilities

## Data Layer

Collect and standardize financial data.

---

## Metrics Layer

Transform raw financial data into financial metrics.

---

## Analysis Layer

Evaluate business quality.

---

## Valuation Layer

Estimate intrinsic value.

---

## Decision Layer

Generate investment decisions.

---

## Application Layer

Provide business use cases.

Examples

Portfolio Engine

Macro Engine

Market Breadth

Realtime

AI

---

# 6. Object Relationships

```
FinancialStatement
│
├── BalanceSheet
│
└── IncomeStatement

↓

FinancialMetrics

↓

MetricResult

↓

FinancialAnalysis

↓

AnalysisResult

↓

FinancialAnalysisResult

↓

Valuation

↓

ValuationResult

↓

Decision

↓

DecisionResult
```

---

# 7. Design Rules

Rule 1

Domain Objects must not contain business logic.

---

Rule 2

Business logic belongs to Services, Metrics, Rules or Engines.

---

Rule 3

Every Domain Object must be immutable whenever practical.

---

Rule 4

All layers communicate using Domain Objects.

---

Rule 5

Future modules must reuse existing Domain Objects.

---

# 8. Future Extensions

Planned Domain Objects

MarketData

MacroData

SectorAnalysis

PortfolioAnalysis

RiskAnalysis

RealtimeSnapshot

AISummary

---

# End of Document