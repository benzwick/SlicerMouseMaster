Preset Format
=============

Technical specification for MouseMaster preset files.

File Format
-----------

Presets are stored as JSON files with UTF-8 encoding.

Schema
------

.. code-block:: json

   {
     "id": "string (required)",
     "name": "string (required)",
     "version": "string (required)",
     "mouseId": "string (required)",
     "author": "string (optional)",
     "description": "string (optional)",
     "mappings": {
       "button_id": {
         "action": "action_id",
         "parameters": {}
       }
     },
     "contextMappings": {
       "ModuleName": {
         "button_id": {
           "action": "action_id",
           "parameters": {}
         }
       }
     }
   }

Required Fields
---------------

id
^^

Unique identifier for the preset.

- Type: ``string``
- Format: lowercase letters, numbers, underscores
- Example: ``"my_workflow_preset"``

name
^^^^

Human-readable display name.

- Type: ``string``
- Example: ``"My Workflow Preset"``

version
^^^^^^^

Preset format version for compatibility.

- Type: ``string``
- Current version: ``"1.0"``

mouseId
^^^^^^^

Target mouse profile identifier.

- Type: ``string``
- Must match an existing mouse profile ID
- Example: ``"logitech_mx_master_3s"``

Optional Fields
---------------

author
^^^^^^

Creator of the preset.

- Type: ``string``
- Example: ``"Your Name"``

description
^^^^^^^^^^^

Brief description of the preset's purpose.

- Type: ``string``
- Example: ``"Optimized for segmentation workflows"``

mappings
^^^^^^^^

Default button-to-action mappings.

- Type: ``object``
- Keys: Button IDs (from mouse profile)
- Values: Mapping objects

contextMappings
^^^^^^^^^^^^^^^

Module-specific binding overrides.

- Type: ``object``
- Keys: Slicer module names (case-sensitive)
- Values: Objects with button-to-mapping pairs

Mapping Object
--------------

Defines what action a button triggers:

.. code-block:: json

   {
     "action": "action_id",
     "parameters": {
       "key": "value"
     }
   }

action
^^^^^^

Action identifier to execute.

- Type: ``string``
- Required: yes
- Example: ``"edit_undo"``

parameters
^^^^^^^^^^

Additional parameters for the action.

- Type: ``object``
- Required: no
- Content depends on action type

Button IDs
----------

Standard button identifiers:

.. list-table::
   :header-rows: 1

   * - ID
     - Description
   * - ``left``
     - Left click (usually not remappable)
   * - ``right``
     - Right click (usually not remappable)
   * - ``middle``
     - Middle click / scroll wheel click
   * - ``back``
     - Back button (thumb area)
   * - ``forward``
     - Forward button (thumb area)
   * - ``thumb``
     - Additional thumb button

Custom button IDs may be defined in mouse profiles.

Module Names
------------

Common Slicer module names for context mappings:

- ``SegmentEditor``
- ``Markups``
- ``VolumeRendering``
- ``Models``
- ``Transforms``
- ``Data``
- ``Volumes``

Module names are case-sensitive and must match exactly.

Complete Example
----------------

.. code-block:: json

   {
     "id": "segmentation_workflow",
     "name": "Segmentation Workflow",
     "version": "1.0",
     "mouseId": "logitech_mx_master_3s",
     "author": "Ben Zwick",
     "description": "Optimized button layout for segmentation tasks",
     "mappings": {
       "back": {
         "action": "edit_undo"
       },
       "forward": {
         "action": "edit_redo"
       },
       "middle": {
         "action": "view_reset_3d"
       },
       "thumb": {
         "action": "view_toggle_crosshair"
       }
     },
     "contextMappings": {
       "SegmentEditor": {
         "back": {
           "action": "segment_previous"
         },
         "forward": {
           "action": "segment_next"
         },
         "thumb": {
           "action": "segment_editor_toggle_effect"
         }
       },
       "Markups": {
         "back": {
           "action": "markups_delete_point"
         },
         "forward": {
           "action": "markups_place_fiducial"
         }
       }
     }
   }

Validation
----------

Presets are validated on load. Validation checks:

1. Required fields present
2. ``mouseId`` references existing profile
3. Button IDs exist in the referenced mouse profile
4. Action IDs are registered
5. JSON syntax is valid

Python Validation
^^^^^^^^^^^^^^^^^

.. code-block:: python

   import json

   with open("preset.json") as f:
       data = json.load(f)

   required = ["id", "name", "version", "mouseId"]
   for field in required:
       assert field in data, f"Missing required field: {field}"

   print("Preset structure valid!")

File Locations
--------------

Built-in presets
^^^^^^^^^^^^^^^^

::

   <Extension>/presets/builtin/

User presets
^^^^^^^^^^^^

::

   # Windows
   %LOCALAPPDATA%/NA-MIC/Slicer X.X-YYYY-MM-DD/MouseMaster/presets/

   # macOS
   ~/Library/Application Support/NA-MIC/Slicer X.X-YYYY-MM-DD/MouseMaster/presets/

   # Linux
   ~/.config/NA-MIC/Slicer X.X-YYYY-MM-DD/MouseMaster/presets/

Migration
---------

When the preset format version changes, MouseMaster will automatically migrate
older presets. The original file is preserved with a ``.bak`` extension.

See Also
--------

- :doc:`/user-guide/presets` - User guide for preset management
- :doc:`actions` - Available action reference
- :doc:`/developer-guide/adding-actions` - Creating custom actions
