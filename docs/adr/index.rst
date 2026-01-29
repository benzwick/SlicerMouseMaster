Architecture Decision Records
=============================

Architecture Decision Records (ADRs) document significant design decisions in
SlicerMouseMaster.

ADR Index
---------

.. list-table::
   :header-rows: 1
   :widths: 10 50 20

   * - ADR
     - Title
     - Status
   * - :doc:`ADR-001-event-interception`
     - Event Interception Strategy
     - Accepted
   * - :doc:`ADR-002-preset-file-format`
     - Preset File Format
     - Accepted
   * - :doc:`ADR-003-button-detection`
     - Button Detection Mechanism
     - Accepted
   * - :doc:`ADR-004-platform-differences`
     - Platform Differences
     - Accepted
   * - :doc:`ADR-005-persistence`
     - Persistence Strategy
     - Accepted
   * - :doc:`ADR-006-ui-framework`
     - UI Framework Choices
     - Accepted
   * - :doc:`ADR-007-preset-sharing`
     - Preset Sharing Mechanism
     - Accepted
   * - :doc:`ADR-008-testing`
     - Testing Strategy
     - Accepted
   * - :doc:`ADR-009-action-mapping`
     - Slicer Action Mapping
     - Accepted
   * - :doc:`ADR-010-context-bindings`
     - Context-Sensitive Bindings
     - Accepted
   * - :doc:`ADR-011-documentation-infrastructure`
     - Documentation Infrastructure
     - Accepted
   * - :doc:`ADR-012-living-documentation`
     - Living Documentation
     - Accepted

What is an ADR?
---------------

An Architecture Decision Record captures a significant architectural decision
along with its context and consequences.

Each ADR includes:

- **Title**: Brief description of the decision
- **Status**: Proposed, Accepted, Deprecated, or Superseded
- **Context**: The situation that led to this decision
- **Decision**: What we decided to do
- **Consequences**: The results of this decision

Creating a New ADR
------------------

1. Copy the template from ``docs/adr/README.md``
2. Name it ``ADR-XXX-short-title.md`` where XXX is the next number
3. Fill in all sections
4. Submit for review via pull request
5. Add to this index once accepted

.. toctree::
   :hidden:

   ADR-001-event-interception
   ADR-002-preset-file-format
   ADR-003-button-detection
   ADR-004-platform-differences
   ADR-005-persistence
   ADR-006-ui-framework
   ADR-007-preset-sharing
   ADR-008-testing
   ADR-009-action-mapping
   ADR-010-context-bindings
   ADR-011-documentation-infrastructure
   ADR-012-living-documentation
