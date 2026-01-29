Available Actions
=================

Complete reference of actions that can be assigned to mouse buttons.

.. note::

   This documentation is auto-generated from the ActionRegistry.
   Run ``test_generate_actions_reference.py`` in Slicer to regenerate.

.. include:: _generated/actions.rst

Action Availability
-------------------

Actions may only be available in certain contexts:

**Always**
  Action works in any module

**Segment Editor**
  Action only works when Segment Editor is active

**When X selected/loaded**
  Action requires specific state (item selected, volume loaded, etc.)

MouseMaster checks availability before executing. Unavailable actions are
silently skipped.

Implementing Custom Actions
---------------------------

See :doc:`/developer-guide/adding-actions` for how to create new actions.
