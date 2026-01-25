# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for SlicerMouseMaster.

## What is an ADR?

An ADR is a document that captures an important architectural decision made along with its context and consequences.

## ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [001](ADR-001-event-interception.md) | Event Interception Strategy | Accepted | 2025-01-25 |
| [002](ADR-002-preset-file-format.md) | Preset File Format | Accepted | 2025-01-25 |
| [003](ADR-003-button-detection.md) | Button Detection Mechanism | Accepted | 2025-01-25 |
| [004](ADR-004-platform-differences.md) | Platform Differences | Accepted | 2025-01-25 |
| [005](ADR-005-persistence.md) | Persistence Strategy | Accepted | 2025-01-25 |
| [006](ADR-006-ui-framework.md) | UI Framework Choices | Accepted | 2025-01-25 |
| [007](ADR-007-preset-sharing.md) | Preset Sharing Mechanism | Accepted | 2025-01-25 |
| [008](ADR-008-testing.md) | Testing Strategy | Accepted | 2025-01-25 |
| [009](ADR-009-action-mapping.md) | Slicer Action Mapping | Accepted | 2025-01-25 |
| [010](ADR-010-context-bindings.md) | Context-Sensitive Bindings | Accepted | 2025-01-25 |

## Status Values

- **Proposed**: Under discussion
- **Accepted**: Approved and in effect
- **Deprecated**: No longer recommended
- **Superseded**: Replaced by another ADR

## Template

```markdown
# ADR-XXX: Title

## Status

Proposed | Accepted | Deprecated | Superseded by ADR-YYY

## Context

What is the issue that we're seeing that is motivating this decision or change?

## Decision

What is the change that we're proposing and/or doing?

## Consequences

What becomes easier or more difficult to do because of this change?

### Positive

- Benefit 1
- Benefit 2

### Negative

- Drawback 1
- Drawback 2

### Neutral

- Trade-off 1

## References

- Link to related documentation
- Link to related ADRs
```

## Creating a New ADR

1. Copy the template above
2. Number sequentially (next is ADR-011)
3. Fill in all sections
4. Add to the index table above
5. Submit for review
