# DMI Platform Coding Standard

Version: 1.0

Status: Official

---

# 1. Purpose

This document defines coding conventions for all DMI Platform modules.

The objective is consistency, readability, maintainability and scalability.

---

# 2. General Principles

Code should be:

- Simple
- Explicit
- Reusable
- Testable
- Documented

Avoid clever code.

Prefer readable code.

---

# 3. File Structure

One file

↓

One responsibility

Example

financial_metrics.py

Only FinancialMetrics

Do not put unrelated classes together.

---

# 4. Class Naming

Use PascalCase

Correct

FinancialMetrics

FinancialStatement

ScoringEngine

ProfitabilityRules

Wrong

financialmetrics

financial_metrics_class

Financialmetrics

---

# 5. Function Naming

Use snake_case

Correct

calculate_score()

get_metric()

margin_of_safety()

evaluate()

Wrong

CalculateScore()

calcScore()

GETMetric()

---

# 6. Variable Naming

Use descriptive snake_case

Correct

current_price

target_pe

discount_rate

operating_profit

Wrong

cp

tp

x

value1

---

# 7. Constant Naming

Use UPPER_CASE

DEFAULT_PE

DEFAULT_DISCOUNT_RATE

MAX_RETRY

---

# 8. Type Hint

Every public method must use type hints.

Correct

```python
def evaluate(
    current_price: float | None
) -> ValuationResult:
```

---

# 9. Docstring

Every public class must have a docstring.

Every public method must have a docstring.

Use Google-style or simple descriptive docstrings.

---

# 10. Imports

Standard Library

↓

Third-party

↓

DMI modules

Example

```python
from dataclasses import dataclass

from dmi_core.metrics import FinancialMetrics
```

Avoid wildcard imports.

Wrong

```python
from module import *
```

---

# 11. Domain Objects

Never return raw dict.

Wrong

```python
return {
    "roe": roe
}
```

Correct

```python
return MetricResult(...)
```

---

# 12. Business Logic

Business logic belongs only to:

Metrics

Rules

Valuation

Decision

AI

Never inside Models.

---

# 13. Error Handling

Missing financial data

↓

Return

```python
value=None
display="N/A"
```

Do not raise exceptions for expected missing values.

---

# 14. Testing

Every module requires

Unit Test

Example

Documentation

Architecture Review

No exceptions.

---

# 15. Examples

Every public module requires

examples/

Example files must execute without modification.

---

# 16. Documentation

Every Sprint must update

CHANGELOG.md

ROADMAP.md

Relevant SPEC files

---

# 17. Repository Rules

No generated files committed.

Ignore

__pycache__/

*.pyc

*.egg-info/

tmp/

logs/

---

# 18. Performance

Avoid duplicated calculations.

Metrics should calculate once.

Higher layers reuse Metrics.

---

# 19. Future Compatibility

Public API changes require

Version update

Documentation update

Migration notes

---

# 20. Philosophy

Readable code is more valuable than clever code.

Architecture is more valuable than shortcuts.

Consistency is more valuable than personal style.

Long-term maintainability is more valuable than short-term speed.

---

End of Document