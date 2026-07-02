# DMI Platform

> **Enterprise Financial Analysis Framework for Vietnam Stock Market**

DMI Platform is a modular financial analysis framework designed for the Vietnam stock market.

The project aims to provide a standardized architecture for collecting, transforming, analyzing and valuing financial data.

---

# Vision

Build an enterprise-grade investment platform that can support:

- Financial Statement Analysis
- Financial Metrics
- Company Valuation
- Stock Screening
- Portfolio Management
- Market Analytics
- AI Investment Assistant

---

# Current Version

```
DMI Platform v2.0.0-RC1
```

Current Status:

- ✅ Data Layer Completed
- 🚧 Release Candidate

---

# Features

## Data Layer

- Enterprise Project Structure
- Base Provider
- CafeF Provider
- CafeF Parser
- Financial Dictionary
- CafeF Mapper
- Domain Models
- Financial Statement Service

## Testing

- Unit Tests
- Integration Tests
- Example Application

---

# Project Structure

```text
DMI_FRAMEWORK/
│
├── dmi_core/
│   ├── config/
│   ├── core/
│   ├── providers/
│   ├── parsers/
│   ├── dictionary/
│   ├── mappers/
│   ├── models/
│   ├── services/
│   ├── metrics/
│   └── ...
│
├── tests/
├── examples/
├── docs/
├── logs/
│
├── README.md
├── CHANGELOG.md
├── ROADMAP.md
├── ARCHITECTURE.md
├── pyproject.toml
└── requirements.txt
```

---

# Architecture

```
Provider
    │
Parser
    │
Dictionary
    │
Mapper
    │
Domain Models
    │
Services
    │
Financial Metrics
    │
Analysis Engines
```

---

# Quick Start

```python
from dmi_core.services import FinancialStatementService

service = FinancialStatementService()

statement = service.get(
    symbol="AAA",
    period="QUY"
)

print(statement.balance_sheet.total_assets)
print(statement.income_statement.net_profit)
```

---

# Roadmap

## Version 2.0

- Enterprise Framework
- Data Layer
- Financial Statement Service

## Version 2.1

- Financial Metrics

## Version 2.2

- Financial Analysis

## Version 2.3

- Valuation Engine

## Version 2.4

- Screening Engine

## Version 3.0

- AI Investment Platform

---

# Design Principles

- Clean Architecture
- Domain Driven Design
- Modular Design
- Test First
- Single Source of Truth
- Enterprise Ready

---

# Author

Nguyen Duc Manh

Investment Analyst & Software Developer

---

# License

MIT License