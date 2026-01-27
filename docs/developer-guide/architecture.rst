Architecture
============

This document describes the internal architecture of SlicerMouseMaster.

System Overview
---------------

::

   ┌─────────────────────────────────────────────────────────────────┐
   │                         Qt Application                          │
   │  ┌───────────────────────────────────────────────────────────┐  │
   │  │              MouseMasterEventHandler                       │  │
   │  │  (Application-level Qt event filter)                       │  │
   │  └───────────────────────────────────────────────────────────┘  │
   │        │                    │                    │              │
   │        ▼                    ▼                    ▼              │
   │  ┌──────────┐        ┌──────────┐        ┌──────────────┐      │
   │  │ Platform │        │  Preset  │        │    Action    │      │
   │  │ Adapter  │        │ Manager  │        │   Registry   │      │
   │  └──────────┘        └──────────┘        └──────────────┘      │
   │        │                    │                    │              │
   │        └────────────────────┼────────────────────┘              │
   │                             ▼                                   │
   │                    ┌──────────────┐                             │
   │                    │ Mouse Profile│                             │
   │                    │  (dataclass) │                             │
   │                    └──────────────┘                             │
   └─────────────────────────────────────────────────────────────────┘

Event Flow
----------

When a user presses a mouse button:

::

   User Button Press
       │
       ▼
   Qt Application (eventFilter)
       │
       ▼
   MouseMasterEventHandler.eventFilter()
       ├── Normalize button via PlatformAdapter
       ├── Get current Slicer module context
       ├── Look up binding: context-specific → default
       ├── Execute action via ActionRegistry
       └── Return True (consumed) or False (pass-through)

Key Classes
-----------

MouseMaster/MouseMaster.py
^^^^^^^^^^^^^^^^^^^^^^^^^^

- **MouseMaster**: Slicer module registration and metadata
- **MouseMasterWidget**: Qt widget for UI setup and user interaction
- **MouseMasterLogic**: Business logic coordinator

MouseMasterLib/EventHandler.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The core of MouseMaster. Implements a Qt application-level event filter that
intercepts mouse button events.

.. code-block:: python

   class MouseMasterEventHandler(QObject):
       def eventFilter(self, obj, event):
           if event.type() == QEvent.MouseButtonPress:
               button = event.button()
               # Normalize and execute mapped action
               return self.handleButton(button)
           return False

MouseMasterLib/MouseProfile.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Data classes for mouse definitions:

- **MouseButton**: Single button definition (id, name, Qt code, remappable)
- **MouseFeatures**: Optional features (horizontal scroll, thumb wheel)
- **MouseProfile**: Complete mouse definition with all buttons

MouseMasterLib/PresetManager.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Handles preset loading, saving, and management:

- **Mapping**: Single button-to-action mapping
- **Preset**: Complete preset with mappings and context overrides
- **PresetManager**: CRUD operations for presets

MouseMasterLib/ActionRegistry.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Singleton registry of executable actions:

.. code-block:: python

   registry = ActionRegistry.get_instance()
   registry.register("my_action", MyActionHandler(), category="custom")
   registry.execute("my_action", parameters={})

MouseMasterLib/PlatformAdapter.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Cross-platform button code normalization:

.. code-block:: python

   adapter = PlatformAdapter.get_instance()
   normalized = adapter.normalize_button(qt_button_code)

MouseMasterLib/ButtonDetector.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Interactive wizard for detecting button codes on unknown mice.

Data Formats
------------

Mouse Definition JSON
^^^^^^^^^^^^^^^^^^^^^

Located in ``Resources/MouseDefinitions/``:

.. code-block:: json

   {
     "id": "logitech_mx_master_3s",
     "name": "Logitech MX Master 3S",
     "vendor": "Logitech",
     "vendorId": "0x46D",
     "productIds": ["0x4082", "0xB023"],
     "buttons": [
       {
         "id": "left",
         "name": "Left Click",
         "qtButton": 1,
         "remappable": false
       },
       {
         "id": "back",
         "name": "Back",
         "qtButton": 8,
         "remappable": true,
         "defaultAction": "undo"
       }
     ],
     "features": {
       "horizontalScroll": true,
       "thumbWheel": true
     }
   }

Preset JSON
^^^^^^^^^^^

Located in ``presets/``:

.. code-block:: json

   {
     "id": "segmentation_workflow",
     "name": "Segmentation Workflow",
     "version": "1.0",
     "mouseId": "logitech_mx_master_3s",
     "mappings": {
       "back": {"action": "slicer_action", "actionId": "undo"},
       "forward": {"action": "slicer_action", "actionId": "redo"}
     },
     "contextMappings": {
       "SegmentEditor": {
         "back": {"action": "segment_previous"},
         "forward": {"action": "segment_next"}
       }
     }
   }

Design Decisions
----------------

Key architectural decisions are documented in Architecture Decision Records
(ADRs):

- :doc:`/adr/index` - Full list of ADRs

Important decisions:

1. **Qt event filter** over VTK observers for broader coverage
2. **JSON presets** for human-readable, shareable configurations
3. **Platform adapters** to abstract OS differences
4. **Singleton registries** for actions and adapters

Qt Button Codes
---------------

Reference for Qt mouse button constants:

.. list-table::
   :header-rows: 1

   * - Qt Button
     - Constant
     - Typical Mapping
   * - 1
     - Qt.LeftButton
     - Primary
   * - 2
     - Qt.RightButton
     - Context menu
   * - 4
     - Qt.MiddleButton
     - Pan/rotate
   * - 8
     - Qt.BackButton
     - Back/undo
   * - 16
     - Qt.ForwardButton
     - Forward/redo
   * - 32
     - Qt.ExtraButton1
     - Custom (thumb)

Modifier Keys
^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Qt Modifier
     - Constant
   * - Shift
     - Qt.ShiftModifier
   * - Ctrl
     - Qt.ControlModifier
   * - Alt
     - Qt.AltModifier
   * - Meta
     - Qt.MetaModifier
