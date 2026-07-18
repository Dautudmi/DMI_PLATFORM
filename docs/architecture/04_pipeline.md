# Pipeline Architecture

Pattern

Analyzer

↓

Pipeline

↓

Stage

↓

Service

↓

Core

Rules

Pipeline orchestrates.

Stage performs one responsibility.

Stage never calls another Stage.

Stage never contains business workflow.

PipelineResult contains execution result.

Context transfers state between stages.