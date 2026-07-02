# Changelog

All notable changes to DMI Platform will be documented in this file.

The format is based on **Keep a Changelog**.

Versioning follows **Semantic Versioning (SemVer)**.

---

# [2.0.0-RC1] - 2026-06

## Overview

The first enterprise release candidate of DMI Platform.

This version establishes the complete Data Layer architecture and serves as the foundation for all future financial analysis modules.

---

## Added

### Core Framework

- Enterprise project structure
- Configuration module
- Core utilities
- Logging structure

### Providers

- BaseProvider interface
- CafeFProvider implementation

### Parsers

- CafeFParser

### Dictionary

- Financial Dictionary
- Standard financial field mapping
- CafeF → DMI field mapping

### Models

- EngineResult
- BalanceSheet
- IncomeStatement
- FinancialStatement

### Mappers

- CafeFMapper
- Domain model mapping

### Services

- FinancialStatementService

### Tests

- Provider tests
- Parser tests
- Mapper tests
- Model tests
- Pipeline tests

### Examples

- Financial Statement Example

### Documentation

- README
- Architecture
- Roadmap
- Changelog

---

## Changed

- Unified financial domain architecture.
- Standardized provider naming.
- Refactored mapper to use Financial Dictionary.
- Standardized FinancialStatement as Aggregate Root.

---

## Fixed

- Fixed provider/schema inconsistency.
- Fixed mapper field alignment.
- Fixed metadata consistency across domain models.
- Improved Data Layer stability.

---

## Architecture

Completed Data Layer:

```text
Provider

↓

Parser

↓

Dictionary

↓

Mapper

↓

Domain Models

↓

Service
```

Status

```
Stable
```

---

## Current Modules

Completed

- Provider Layer
- Parser Layer
- Dictionary Layer
- Mapper Layer
- Domain Models
- Service Layer

---

## Known Limitations

The following modules are not included in this release:

- Financial Metrics
- Financial Analysis
- Valuation Engine
- Screening Engine
- Portfolio Engine
- Market Intelligence
- AI Platform

---

## Next Version

### Version 2.1.0

Planned Features

- Financial Metrics
- ROE
- ROA
- Current Ratio
- Quick Ratio
- Gross Margin
- Net Margin
- Asset Turnover
- EPS
- BVPS

---

# Version History

| Version | Status |
|----------|--------|
| 2.0.0-RC1 | Release Candidate |
| 2.1.0 | Planned |
| 2.2.0 | Planned |
| 2.3.0 | Planned |
| 2.4.0 | Planned |
| 3.0.0 | Planned |