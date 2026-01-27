Context-Sensitive Bindings
==========================

Context-sensitive bindings allow different button mappings depending on which
Slicer module is currently active.

How It Works
------------

When you press a button, MouseMaster:

1. Detects the currently active Slicer module
2. Checks for a context-specific binding for that module
3. If found, uses the context binding
4. Otherwise, uses the default binding

Example: The Back button could trigger Undo in most modules, but switch to
"Previous Segment" when in Segment Editor.

Setting Up Context Bindings
---------------------------

1. Open the **Button Mappings** section
2. Check "Enable context-sensitive bindings"
3. Select a context from the dropdown (e.g., "Segment Editor")
4. Configure button mappings for that context
5. Repeat for other modules as needed

Supported Contexts
------------------

MouseMaster recognizes these Slicer modules for context bindings:

.. list-table::
   :header-rows: 1

   * - Module
     - Context ID
     - Typical Use Case
   * - Segment Editor
     - ``SegmentEditor``
     - Segmentation workflows
   * - Markups
     - ``Markups``
     - Fiducial and curve placement
   * - Volume Rendering
     - ``VolumeRendering``
     - 3D visualization
   * - Models
     - ``Models``
     - Surface model viewing
   * - Transforms
     - ``Transforms``
     - Transform editing
   * - Default
     - (fallback)
     - All other modules

Example Configuration
---------------------

A segmentation-focused preset might have:

**Default bindings:**

- Back: Undo
- Forward: Redo
- Thumb: Toggle Crosshair

**Segment Editor overrides:**

- Back: Previous Segment
- Forward: Next Segment
- Thumb: Toggle Paint/Erase

This way, your familiar undo/redo shortcuts work everywhere, but in Segment
Editor you get quick segment navigation.

Best Practices
--------------

1. **Keep defaults intuitive**: Use common actions (undo, redo) as defaults
2. **Override sparingly**: Only add context bindings where truly needed
3. **Group related actions**: Put segment operations on adjacent buttons
4. **Test thoroughly**: Switch between modules to verify bindings work

Preset Format
-------------

Context bindings are stored in the ``contextMappings`` section of presets:

.. code-block:: json

   {
     "mappings": {
       "back": {"action": "edit_undo"},
       "forward": {"action": "edit_redo"}
     },
     "contextMappings": {
       "SegmentEditor": {
         "back": {"action": "segment_previous"},
         "forward": {"action": "segment_next"}
       },
       "Markups": {
         "back": {"action": "markups_delete_point"},
         "forward": {"action": "markups_place_fiducial"}
       }
     }
   }

See Also
--------

- :doc:`button-mapping` - Configure individual buttons
- :doc:`presets` - Save context-sensitive configurations
- :doc:`/reference/actions` - Complete action reference
