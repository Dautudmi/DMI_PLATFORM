# Framework Overview

## Goal

Build a reusable Financial Intelligence Framework.

The framework consists of two major parts.

- dmi_core
- apps

## dmi_core

Pure financial intelligence.

Contains:

- Financial Statement
- Metrics
- Rules
- Analysis
- Valuation
- Decision
- DMI Engine

No application logic.

No UI.

No CSV.

No Database.

## apps

Business applications built on top of dmi_core.

Contains:

- Portfolio
- Watchlist
- Realtime
- Client

Apps coordinate workflows.

Apps never implement financial intelligence.