Slicer API Quick Reference
==========================

Common Slicer API patterns used by SlicerMouseMaster.

Get Current Module
------------------

.. code-block:: python

   current = slicer.app.moduleManager().currentModule()

Trigger Menu Action
-------------------

.. code-block:: python

   mainWindow = slicer.util.mainWindow()
   action = mainWindow.findChild(qt.QAction, "actionName")
   action.trigger()

Access Segment Editor
---------------------

.. code-block:: python

   editor = slicer.modules.SegmentEditorWidget.editor
   editor.setActiveEffectByName("Paint")

Settings Persistence
--------------------

.. code-block:: python

   settings = qt.QSettings()
   settings.setValue("MouseMaster/Key", value)
   value = settings.value("MouseMaster/Key", default)

Module Reload
-------------

.. code-block:: python

   import MouseMaster
   slicer.util.reloadScriptedModule('MouseMaster')

Official Documentation
----------------------

- `Slicer Developer Guide <https://slicer.readthedocs.io/en/latest/developer_guide/>`_
- `Slicer Script Repository <https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html>`_
