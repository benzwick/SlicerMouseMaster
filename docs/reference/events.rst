Qt Events Reference
===================

This page documents Qt button constants and modifier keys used by SlicerMouseMaster.

Qt Button Constants
-------------------

.. list-table::
   :header-rows: 1
   :widths: 15 25 30

   * - Qt Button
     - Constant
     - Typical Mapping
   * - 1
     - ``Qt.LeftButton``
     - Primary click
   * - 2
     - ``Qt.RightButton``
     - Context menu
   * - 4
     - ``Qt.MiddleButton``
     - Pan/rotate
   * - 8
     - ``Qt.BackButton``
     - Back/undo
   * - 16
     - ``Qt.ForwardButton``
     - Forward/redo
   * - 32
     - ``Qt.ExtraButton1``
     - Custom (thumb)

Modifier Keys
-------------

.. list-table::
   :header-rows: 1
   :widths: 20 30

   * - Qt Modifier
     - Constant
   * - Shift
     - ``Qt.ShiftModifier``
   * - Ctrl
     - ``Qt.ControlModifier``
   * - Alt
     - ``Qt.AltModifier``
   * - Meta
     - ``Qt.MetaModifier``

Event Flow
----------

When a mouse button is pressed:

1. Qt Application receives the event via ``eventFilter``
2. ``MouseMasterEventHandler.eventFilter()`` processes it:

   - Normalizes button via ``PlatformAdapter``
   - Gets current Slicer module context
   - Looks up binding: context-specific first, then default
   - Executes action via ``ActionRegistry``
   - Returns ``True`` (consumed) or ``False`` (pass-through)
