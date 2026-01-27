Adding Actions
==============

This guide explains how to add new actions to MouseMaster's action registry.

Overview
--------

Actions are operations that can be triggered by mouse button presses. MouseMaster
provides a registry of built-in actions and supports custom action registration.

Action Types
------------

**Built-in Actions**
  Pre-registered actions for common Slicer operations (undo, redo, etc.)

**Custom Actions**
  User-defined actions including Python commands, keyboard shortcuts, and
  menu triggers.

Registering a New Action
------------------------

1. Create an Action Handler
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Action handlers inherit from ``ActionHandler`` and implement the ``execute``
method:

.. code-block:: python

   from MouseMasterLib.ActionRegistry import ActionHandler, ActionRegistry

   class MyCustomAction(ActionHandler):
       """Handler for my custom action."""

       def execute(self, parameters: dict | None = None) -> bool:
           """Execute the action.

           Args:
               parameters: Optional parameters from preset configuration

           Returns:
               True if action executed successfully, False otherwise
           """
           # Your action logic here
           print("My custom action executed!")
           return True

       def is_available(self) -> bool:
           """Check if this action can be executed.

           Returns:
               True if action is available in current context
           """
           # Optional: Return False if action shouldn't be available
           return True

2. Register the Action
^^^^^^^^^^^^^^^^^^^^^^

Register your action with the ActionRegistry singleton:

.. code-block:: python

   registry = ActionRegistry.get_instance()
   registry.register(
       action_id="my_custom_action",
       handler=MyCustomAction(),
       category="custom",
       description="Does something useful"
   )

3. Use in Presets
^^^^^^^^^^^^^^^^^

Your action can now be used in preset mappings:

.. code-block:: json

   {
     "mappings": {
       "back": {"action": "my_custom_action"}
     }
   }

Action Categories
-----------------

Group actions by category for organization:

- ``navigation``: View manipulation (reset, zoom, pan)
- ``editing``: Edit operations (undo, redo, delete)
- ``segmentation``: Segment Editor specific
- ``markups``: Markup operations
- ``custom``: User-defined actions

Built-in Action Examples
------------------------

Undo Action
^^^^^^^^^^^

.. code-block:: python

   class UndoAction(ActionHandler):
       def execute(self, parameters=None):
           mainWindow = slicer.util.mainWindow()
           action = mainWindow.findChild(qt.QAction, "actionEditUndo")
           if action:
               action.trigger()
               return True
           return False

Segment Editor Effect
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   class SegmentEditorEffectAction(ActionHandler):
       def execute(self, parameters=None):
           effect_name = parameters.get("effectName", "Paint")
           editor = slicer.modules.SegmentEditorWidget.editor
           editor.setActiveEffectByName(effect_name)
           return True

       def is_available(self):
           # Only available in Segment Editor
           current = slicer.app.moduleManager().currentModule()
           return current == "SegmentEditor"

Python Command Action
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   class PythonCommandAction(ActionHandler):
       def execute(self, parameters=None):
           command = parameters.get("command", "")
           if command:
               exec(command)
               return True
           return False

Keyboard Shortcut Action
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   class KeyboardShortcutAction(ActionHandler):
       def execute(self, parameters=None):
           key = parameters.get("key", "")
           modifiers = parameters.get("modifiers", [])

           # Build key sequence
           sequence = "+".join(modifiers + [key])
           shortcut = qt.QKeySequence(sequence)

           # Send key event
           event = qt.QKeyEvent(qt.QEvent.KeyPress, shortcut[0], qt.Qt.NoModifier)
           qt.QCoreApplication.sendEvent(slicer.util.mainWindow(), event)
           return True

Best Practices
--------------

1. **Check availability**: Implement ``is_available()`` for context-sensitive actions

2. **Handle errors gracefully**: Return ``False`` on failure, don't raise exceptions

3. **Log appropriately**: Use logging for debugging, not print statements

4. **Document parameters**: Describe expected parameters in docstrings

5. **Test thoroughly**: Add unit tests for new actions

Testing Actions
---------------

Unit test your action handler:

.. code-block:: python

   import pytest
   from MouseMasterLib.ActionRegistry import ActionRegistry

   def test_my_action_executes():
       registry = ActionRegistry.get_instance()
       result = registry.execute("my_custom_action")
       assert result is True

   def test_my_action_with_parameters():
       registry = ActionRegistry.get_instance()
       result = registry.execute("my_custom_action", {"param": "value"})
       assert result is True

Discovering Slicer Actions
--------------------------

To find available Slicer menu actions:

.. code-block:: python

   # List all QAction objects in main window
   mainWindow = slicer.util.mainWindow()
   for action in mainWindow.findChildren(qt.QAction):
       print(f"{action.objectName()}: {action.text()}")

Common action names:

- ``actionEditUndo`` - Edit > Undo
- ``actionEditRedo`` - Edit > Redo
- ``actionViewLayoutConventional`` - View > Layout > Conventional
- ``actionFileExit`` - File > Exit

See Also
--------

- :doc:`/reference/actions` - Complete action reference
- :doc:`architecture` - ActionRegistry internals
