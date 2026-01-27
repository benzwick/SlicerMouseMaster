Available Actions
=================

Complete reference of actions that can be assigned to mouse buttons.

Navigation Actions
------------------

.. list-table::
   :header-rows: 1
   :widths: 25 50 25

   * - Action ID
     - Description
     - Availability
   * - ``view_reset_3d``
     - Reset 3D view to default orientation
     - Always
   * - ``view_zoom_in``
     - Zoom in the active view
     - Always
   * - ``view_zoom_out``
     - Zoom out the active view
     - Always
   * - ``view_center_crosshair``
     - Center view on crosshair position
     - Always
   * - ``view_toggle_crosshair``
     - Toggle crosshair visibility
     - Always

Edit Actions
------------

.. list-table::
   :header-rows: 1
   :widths: 25 50 25

   * - Action ID
     - Description
     - Availability
   * - ``edit_undo``
     - Undo last action
     - Always
   * - ``edit_redo``
     - Redo last undone action
     - Always
   * - ``edit_delete_selected``
     - Delete selected item
     - When item selected

Segment Editor Actions
----------------------

.. list-table::
   :header-rows: 1
   :widths: 25 50 25

   * - Action ID
     - Description
     - Availability
   * - ``segment_editor_paint``
     - Activate Paint effect
     - Segment Editor
   * - ``segment_editor_erase``
     - Activate Erase effect
     - Segment Editor
   * - ``segment_editor_toggle_effect``
     - Toggle between Paint and Erase
     - Segment Editor
   * - ``segment_next``
     - Select next segment
     - Segment Editor
   * - ``segment_previous``
     - Select previous segment
     - Segment Editor
   * - ``segment_toggle_visibility``
     - Toggle current segment visibility
     - Segment Editor

Markups Actions
---------------

.. list-table::
   :header-rows: 1
   :widths: 25 50 25

   * - Action ID
     - Description
     - Availability
   * - ``markups_place_fiducial``
     - Start placing fiducial points
     - Always
   * - ``markups_delete_point``
     - Delete last placed control point
     - When markup selected
   * - ``markups_cancel_placement``
     - Cancel current placement mode
     - When placing

Volume Rendering Actions
------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 50 25

   * - Action ID
     - Description
     - Availability
   * - ``volumerendering_toggle``
     - Toggle volume rendering visibility
     - When volume loaded

Custom Action Types
-------------------

Python Command
^^^^^^^^^^^^^^

Execute arbitrary Python code:

.. code-block:: json

   {
     "action": "python_command",
     "parameters": {
       "command": "slicer.util.selectModule('SegmentEditor')"
     }
   }

**Parameters:**

- ``command`` (string, required): Python code to execute

**Security Note:** Be cautious with user-provided Python commands.

Keyboard Shortcut
^^^^^^^^^^^^^^^^^

Simulate a keyboard shortcut:

.. code-block:: json

   {
     "action": "keyboard_shortcut",
     "parameters": {
       "key": "Z",
       "modifiers": ["ctrl"]
     }
   }

**Parameters:**

- ``key`` (string, required): Key to press
- ``modifiers`` (array, optional): Modifier keys (``ctrl``, ``shift``, ``alt``, ``meta``)

Slicer Menu Action
^^^^^^^^^^^^^^^^^^

Trigger a Slicer menu action by name:

.. code-block:: json

   {
     "action": "slicer_menu_EditUndo",
     "actionId": "EditUndo"
   }

**Finding Action Names:**

In Slicer Python console:

.. code-block:: python

   mainWindow = slicer.util.mainWindow()
   for action in mainWindow.findChildren(qt.QAction):
       if action.text():
           print(f"{action.objectName()}: {action.text()}")

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
