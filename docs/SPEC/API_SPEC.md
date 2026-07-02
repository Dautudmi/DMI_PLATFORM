# DMI Platform API Specification

Version: 1.0

Status: Official

---

# 1. Purpose

This document defines all stable public APIs of the DMI Platform.

Public APIs are considered stable after release.

Breaking changes must be avoided.

---

# 2. Public API Rules

Rule 1

Only documented APIs are public.

---

Rule 2

Public APIs must remain backward compatible.

---

Rule 3

Internal modules may change.

Public APIs should not.

---

# 3. Data Layer API

## FinancialStatementService

### get()

```python
statement = service.get(
    symbol="AAA",
    period="QUY",
    page_size=4,
)
```

Returns

```python
FinancialStatement
```

---

# 4. Metrics Layer API

## FinancialMetrics

Initialization

```python
metrics = FinancialMetrics(statement)
```

Stable APIs

```python
metrics.roe()

metrics.roa()

metrics.debt_to_equity()

metrics.all()
```

Future APIs

```python
metrics.get("ROE")

metrics.get("EPS")

metrics.get("BVPS")
```

Return Type

```python
MetricResult
```

---

# 5. Rules Layer API

Every Rule follows

```python
evaluate(...)
```

Example

```python
ProfitabilityRules.evaluate(roe)

LeverageRules.evaluate(debt_to_equity)
```

Return

```python
AnalysisResult
```

---

# 6. Analysis Layer API

Initialization

```python
analysis = FinancialAnalysis(statement)
```

Stable APIs

```python
analysis.profitability()

analysis.leverage()

analysis.summary()

analysis.analyze()
```

Return

```python
FinancialAnalysisResult
```

---

# 7. Scoring API

```python
ScoringEngine.evaluate(results)
```

Return

```python
overall_score

overall_rating

recommendation
```

---

# 8. Valuation API

Initialization

```python
valuation = PEValuation(
    statement,
    config,
)
```

Evaluation

```python
result = valuation.evaluate(
    current_price=35.5,
)
```

Return

```python
ValuationResult
```

---

# 9. Future Valuation APIs

PBValuation

DCFValuation

EVEBITDAValuation

DividendValuation

ResidualIncomeValuation

---

# 10. Decision API (Future)

```python
decision = DecisionEngine.evaluate(
    analysis,
    valuation,
)
```

Return

```python
DecisionResult
```

---

# 11. AI API (Future)

```python
report = AIEngine.generate(
    analysis,
    valuation,
    decision,
)
```

---

# 12. API Stability Levels

Stable

FinancialStatementService

FinancialMetrics

FinancialAnalysis

ScoringEngine

Experimental

Valuation

Decision

AI

---

# 13. API Naming Convention

Methods

snake_case

Classes

PascalCase

Modules

snake_case

Constants

UPPER_CASE

---

# 14. Error Handling

Missing data

↓

Return

```python
MetricResult(
    value=None,
    display="N/A"
)
```

Never raise exceptions for normal missing financial data.

---

# 15. Future APIs

Market API

Macro API

Portfolio API

Realtime API

AI API

---

# End of Document