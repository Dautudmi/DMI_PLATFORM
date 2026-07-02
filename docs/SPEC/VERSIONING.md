# DMI Platform Versioning Policy

Version: 1.0

Status: Official

---

# 1. Purpose

This document defines the official versioning strategy of the DMI Platform.

All releases must follow Semantic Versioning (SemVer).

---

# 2. Semantic Versioning

DMI uses the format:

MAJOR.MINOR.PATCH

Example

2.2.0

Where

MAJOR

Breaking architecture changes

MINOR

New functionality without breaking compatibility

PATCH

Bug fixes, documentation updates and small improvements

---

# 3. Major Version

Examples

1.0.0

2.0.0

3.0.0

Increment when

Architecture changes

Public APIs change

Breaking compatibility

Examples

New Platform Architecture

Decision Engine

AI Platform

---

# 4. Minor Version

Examples

2.2.0

2.3.0

2.4.0

Increment when

New modules

New metrics

New valuation models

New rules

No breaking changes

---

# 5. Patch Version

Examples

2.2.1

2.2.2

2.2.3

Increment when

Bug fixes

Performance improvements

Documentation updates

Code cleanup

No API changes

---

# 6. API Stability

Stable APIs

FinancialStatementService

FinancialMetrics

FinancialAnalysis

ScoringEngine

Experimental APIs

Valuation

Decision

AI

Experimental APIs may change between Minor releases.

Stable APIs may only change in Major releases.

---

# 7. Release Lifecycle

Prototype

↓

Internal Testing

↓

Stable Release

↓

Long-Term Support (LTS)

↓

Maintenance

↓

Deprecated

↓

Archived

---

# 8. Long-Term Support

LTS versions are recommended for production systems.

Examples

Portfolio Engine

Market Breadth Engine

Macro Engine

Realtime Engine

AI Platform

Only LTS versions should be used.

---

# 9. Deprecation Policy

Deprecated APIs

Remain available for at least one Minor release.

Documentation must include

Replacement API

Migration examples

Removal schedule

---

# 10. Migration Policy

Every Major release requires

Migration Guide

Updated Examples

Updated Documentation

Repository Review

---

# 11. Git Tag Convention

Examples

v2.2.0

v2.3.0

v3.0.0

Release Candidate

v3.0.0-rc1

v3.0.0-rc2

Stable

v3.0.0

---

# 12. Repository Milestones

Prototype

Internal Framework

Stable Framework

Financial Intelligence Platform

Enterprise Platform

---

# 13. DMI Roadmap

Version 1.x

Foundation

Version 2.x

Stable Framework

Version 3.x

Financial Intelligence

Version 4.x

Enterprise Ecosystem

---

# 14. Release Principles

Architecture First

Documentation First

Testing First

Examples First

Release Last

Code alone is never considered a release.

---

# 15. Current Status

Current Official Version

DMI Platform 2.2.0

Status

Stable Framework

Next Planned Release

2.3.0

Metric Registry

Financial Dictionary Integration

Valuation Foundation

---

End of Document