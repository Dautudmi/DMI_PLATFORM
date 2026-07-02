# DMI Platform Release Policy

Version: 1.0

Status: Official

---

# 1. Purpose

This document defines the official release process of the DMI Platform.

Every release must follow this policy.

No exceptions.

---

# 2. Release Philosophy

DMI prioritizes

Correctness

↓

Stability

↓

Maintainability

↓

Features

Features are never more important than architecture.

---

# 3. Release Types

## Major Release

Example

3.0.0

Characteristics

Breaking API changes

Architecture redesign

New Platform Capability

Requires

Migration Guide

Architecture Review

Full Regression Test

---

## Minor Release

Example

2.3.0

Characteristics

New Features

No breaking changes

Backward Compatible

Requires

Unit Test

Examples

Documentation

---

## Patch Release

Example

2.2.1

Characteristics

Bug Fix

Performance Improvement

Documentation Update

No API Change

---

# 4. Release Workflow

Specification

↓

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

Repository Review

↓

Release

Every stage must PASS.

---

# 5. Release Checklist

Every release must verify

Architecture

Public API

Documentation

Examples

Tests

Version

Changelog

Roadmap

Repository Cleanliness

Only then may the release proceed.

---

# 6. Repository Cleanliness

Before every release

Delete

__pycache__/

*.pyc

*.egg-info/

Temporary files

Unused scripts

Old reports

Repository must be clean.

---

# 7. Public API Freeze

Stable APIs must not change.

Examples

FinancialStatementService.get()

FinancialMetrics

FinancialAnalysis

ScoringEngine

Breaking changes require

Major Version

Migration Guide

---

# 8. Documentation Requirements

Every release updates

README.md

CHANGELOG.md

ROADMAP.md

Relevant SPEC documents

Documentation is part of the release.

---

# 9. Testing Requirements

Every release requires

Unit Tests

Integration Tests (when applicable)

Examples

Manual Verification

All tests must PASS.

---

# 10. Example Requirements

Every public module must include

At least one runnable example.

Examples must work without modification.

---

# 11. Version Control

Every release updates

VERSION

CHANGELOG

Git Tag

Recommended Git Tag

v2.2.0

v2.3.0

v3.0.0

---

# 12. Rollback Policy

If release fails

↓

Rollback immediately

↓

Investigate

↓

Fix

↓

Retest

↓

Release again

Never patch directly in production.

---

# 13. Long-term Support

Stable releases become LTS candidates.

Only stable releases may be used by

Portfolio Engine

Market Breadth Engine

Macro Engine

Realtime Engine

AI Platform

---

# 14. Quality Gate

Release is allowed only when

Architecture Approved

All Tests PASS

Examples PASS

Documentation Updated

Repository Clean

Version Updated

Checklist Completed

---

# 15. Definition of Release

A release is not code.

A release is

Architecture

+

Code

+

Tests

+

Examples

+

Documentation

+

Repository

+

Version

Only then is a release considered complete.

---

End of Document