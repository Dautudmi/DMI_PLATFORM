# DMI Platform Development Standard (DPDS)

Version: 1.0

Status: Official

Author: DMI Platform

---

# 1. Purpose

The DMI Platform Development Standard (DPDS) defines the engineering principles, architecture rules, coding standards, testing workflow and release process for every module developed within the DMI Platform.

Every developer contributing to DMI must follow this document.

---

# 2. Vision

DMI is not a collection of Python scripts.

DMI is a Financial Intelligence Platform.

Its mission is to become the core platform powering:

- Financial Analysis
- Valuation
- Portfolio Management
- Market Breadth
- Macro Analysis
- Realtime Monitoring
- AI Investment Assistant

---

# 3. Core Principles

## Principle 1

Single Source of Truth

Every financial metric must be calculated only once.

Example

ROE

↓

FinancialMetrics

NOT

Rules

NOT

Valuation

NOT

AI

---

## Principle 2

Layer Responsibility

Each layer has exactly one responsibility.

Data Layer

↓

Collect data

Metrics Layer

↓

Calculate metrics

Analysis Layer

↓

Evaluate business quality

Valuation Layer

↓

Estimate intrinsic value

Decision Layer

↓

Generate investment decision

AI Layer

↓

Explain and communicate

---

## Principle 3

No Circular Dependency

Dependency must always flow downward.

Provider

↓

Parser

↓

Mapper

↓

Models

↓

Metrics

↓

Rules

↓

Analysis

↓

Scoring

↓

Valuation

↓

Decision

↓

Applications

No layer may import a higher layer.

---

## Principle 4

Business Rules are Centralized

Business rules must only exist inside Rules Engine.

Analysis classes must never hardcode thresholds.

Wrong

if roe > 20:

Correct

ProfitabilityRules.evaluate()

---

## Principle 5

Configuration must be separated from Logic.

Wrong

target_pe = 10

Correct

ValuationConfig.target_pe

---

# 4. Architecture

Every module follows the same lifecycle.

Specification

↓

Architecture

↓

Implementation

↓

Unit Test

↓

Example

↓

Documentation

↓

Release

No module may skip these steps.

---

# 5. Public API Policy

Public APIs are considered stable.

Examples

FinancialStatementService.get()

FinancialMetrics.roe()

FinancialAnalysis.analyze()

ScoringEngine.evaluate()

Future changes must remain backward compatible whenever possible.

---

# 6. Domain Objects

Every layer communicates through Domain Objects.

Never return raw dictionaries.

Preferred

MetricResult

AnalysisResult

FinancialAnalysisResult

ValuationResult

Future

DecisionResult

---

# 7. Testing Standard

Every new module must include

Unit Test

Example

Documentation

Architecture Review

A Sprint is considered complete only after all four are finished.

---

# 8. Documentation Standard

Each major module requires documentation.

Architecture

Example

API

Domain Model

Future Roadmap

Documentation is considered part of the product.

---

# 9. Naming Convention

Classes

PascalCase

FinancialMetrics

ScoringEngine

ValuationResult

Methods

snake_case

calculate_score()

evaluate()

summary()

Variables

snake_case

current_price

target_pe

margin_of_safety

Constants

UPPER_CASE

DEFAULT_PE

DEFAULT_DISCOUNT_RATE

---

# 10. Repository Structure

DMI Platform follows the following layout.

docs/

examples/

tests/

dmi_core/

Applications

AI

Specifications

Every folder has a single responsibility.

---

# 11. Release Workflow

Architecture Review

↓

Implementation

↓

Unit Test

↓

Example

↓

Documentation

↓

Release

Every release must pass all six stages.

---

# 12. Design Philosophy

DMI values

Correctness over speed

Architecture over shortcuts

Reusability over duplication

Domain Models over dictionaries

Composition over hardcoding

Stability over rapid feature growth

---

# 13. Long-term Goal

The DMI Platform will become the foundation for

Portfolio Engine

Market Breadth Engine

Macro Engine

Realtime Engine

Valuation Engine

Screening Engine

AI Investment Assistant

All future products must build upon DMI Core.

---

# 14. Definition of Done

A Sprint is DONE only if

Architecture approved

Code implemented

Unit Tests pass

Examples run successfully

Documentation completed

Repository reviewed

Only then may the version be released.

---

End of Document