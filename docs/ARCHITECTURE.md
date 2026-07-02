# DMI Platform Architecture

> Enterprise Financial Analysis Platform for Vietnam Stock Market

Version: 2.0.0-RC1

---

# Overview

DMI Platform is designed using a layered architecture.

Each layer has a single responsibility and communicates only with adjacent layers.

This architecture provides:

- High maintainability
- Extensibility
- Testability
- Provider independence
- Domain-driven design

---

# Architecture Overview

```text
                    External APIs
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
     CafeF API                       Future Providers
                                        (SSI, TCBS, Fiin...)
                          │
                          ▼
                    Provider Layer
                          │
                          ▼
                     Parser Layer
                          │
                          ▼
                  Financial Dictionary
                          │
                          ▼
                    Mapper Layer
                          │
                          ▼
                    Domain Models
                          │
                          ▼
                     Service Layer
                          │
                          ▼
                   Financial Metrics
                          │
                          ▼
                  Analysis Engines
        ┌──────────┬──────────┬──────────┐
        │          │          │          │
   Valuation   Screening  Portfolio    AI
```

---

# Layer Responsibilities

## Provider Layer

Responsible for downloading raw financial data.

Responsibilities

- HTTP Request
- Authentication (future)
- Retry
- Timeout

Output

Raw JSON

---

## Parser Layer

Responsible for converting raw provider data into a standard tabular format.

Responsibilities

- Parse JSON
- Normalize structure

Output

Pandas DataFrame

---

## Dictionary Layer

Single Source of Truth.

Responsibilities

- Standard field definitions
- Provider mapping
- Financial terminology

Output

DMI Standard Financial Fields

---

## Mapper Layer

Responsible for converting DataFrames into Domain Models.

Responsibilities

- Data transformation
- Field mapping

Output

BalanceSheet

IncomeStatement

FinancialStatement

---

## Domain Layer

Core business objects.

Current Models

- BalanceSheet
- IncomeStatement
- FinancialStatement

Future

- CashFlowStatement
- CompanyProfile

---

## Service Layer

High-level API for the entire platform.

Responsibilities

- Coordinate Provider
- Coordinate Parser
- Coordinate Mapper

Output

FinancialStatement

Example

```python
service = FinancialStatementService()

statement = service.get("AAA")
```

---

## Metrics Layer

Financial calculation layer.

Future metrics include

- ROE
- ROA
- Current Ratio
- Quick Ratio
- Debt Ratio
- Gross Margin
- Net Margin
- EPS
- BVPS

---

## Analysis Engines

Business logic.

Modules

- Valuation Engine
- Screening Engine
- Portfolio Engine
- Macro Engine
- Market Breadth Engine
- Realtime Engine
- AI Engine

---

# Design Principles

The platform follows these principles:

- Clean Architecture
- Domain Driven Design (DDD)
- Single Responsibility Principle
- Dependency Inversion
- Test First
- Single Source of Truth
- Modular Design

---

# Data Flow

```text
CafeF API

↓

Provider

↓

Parser

↓

Dictionary

↓

Mapper

↓

FinancialStatement

↓

FinancialStatementService

↓

FinancialMetrics

↓

Analysis Engine
```

---

# Project Structure

```text
DMI_PLATFORM/

├── dmi_core/
│
├── tests/
│
├── examples/
│
├── docs/
│
├── logs/
│
├── README.md
├── CHANGELOG.md
├── ROADMAP.md
├── VERSION
├── LICENSE
└── pyproject.toml
```

---

# Version History

| Version | Status |
|----------|--------|
| 2.0.0-RC1 | Data Layer Completed |
| 2.1.0 | Financial Metrics |
| 2.2.0 | Financial Analysis |
| 2.3.0 | Valuation Engine |
| 2.4.0 | Screening Engine |
| 3.0.0 | AI Investment Platform |

---

# Long-term Vision

Build the most complete enterprise financial analysis platform for the Vietnam stock market.

The platform aims to become the foundation for:

- Financial Analytics
- Company Valuation
- Portfolio Management
- Market Intelligence
- AI Investment Assistant