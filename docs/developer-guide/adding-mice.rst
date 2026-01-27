Adding Mouse Profiles
=====================

This guide explains how to add support for new mouse models.

Overview
--------

Mouse profiles define the buttons available on a specific mouse model, including
their Qt button codes and whether they can be remapped.

Creating a Profile
------------------

1. Create JSON Definition
^^^^^^^^^^^^^^^^^^^^^^^^^

Create a new file in ``Resources/MouseDefinitions/``:

.. code-block:: json

   {
     "id": "vendor_model_name",
     "name": "Vendor Model Name",
     "vendor": "Vendor",
     "vendorId": "0x1234",
     "productIds": ["0xABCD"],
     "buttons": [
       {
         "id": "left",
         "name": "Left Click",
         "qtButton": 1,
         "remappable": false
       },
       {
         "id": "right",
         "name": "Right Click",
         "qtButton": 2,
         "remappable": false
       },
       {
         "id": "middle",
         "name": "Middle Click",
         "qtButton": 4,
         "remappable": true,
         "defaultAction": "view_reset_3d"
       },
       {
         "id": "back",
         "name": "Back",
         "qtButton": 8,
         "remappable": true,
         "defaultAction": "edit_undo"
       },
       {
         "id": "forward",
         "name": "Forward",
         "qtButton": 16,
         "remappable": true,
         "defaultAction": "edit_redo"
       }
     ],
     "features": {
       "horizontalScroll": false,
       "thumbWheel": false
     }
   }

2. Add Default Preset
^^^^^^^^^^^^^^^^^^^^^

Create a default preset in ``presets/builtin/``:

.. code-block:: json

   {
     "id": "default_vendor_model",
     "name": "Default (Vendor Model)",
     "version": "1.0",
     "mouseId": "vendor_model_name",
     "mappings": {
       "middle": {"action": "view_reset_3d"},
       "back": {"action": "edit_undo"},
       "forward": {"action": "edit_redo"}
     }
   }

3. Update Documentation
^^^^^^^^^^^^^^^^^^^^^^^

Add the mouse to the supported mice table in:

- ``README.md``
- ``docs/user-guide/index.rst``

Profile Fields Reference
------------------------

Required Fields
^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - ``id``
     - string
     - Unique identifier (lowercase, underscores)
   * - ``name``
     - string
     - Human-readable name
   * - ``buttons``
     - array
     - Button definitions

Optional Fields
^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - ``vendor``
     - string
     - Manufacturer name
   * - ``vendorId``
     - string
     - USB vendor ID (hex)
   * - ``productIds``
     - array
     - USB product IDs (hex)
   * - ``features``
     - object
     - Optional hardware features

Button Fields
^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - ``id``
     - string
     - Unique button identifier
   * - ``name``
     - string
     - Human-readable name
   * - ``qtButton``
     - integer
     - Qt button code
   * - ``remappable``
     - boolean
     - Whether button can be customized
   * - ``defaultAction``
     - string
     - Optional default action ID

Finding Button Codes
--------------------

Use the Button Detection Wizard
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The easiest way to find button codes:

1. Open MouseMaster in Slicer
2. Click "Detect New Mouse..."
3. Press each button when prompted
4. Note the detected Qt button codes

Manual Detection
^^^^^^^^^^^^^^^^

In Slicer's Python console:

.. code-block:: python

   from PySide2.QtCore import QEvent
   from PySide2.QtWidgets import QApplication

   class ButtonDetector:
       def eventFilter(self, obj, event):
           if event.type() == QEvent.MouseButtonPress:
               print(f"Button pressed: {event.button()}")
           return False

   detector = ButtonDetector()
   QApplication.instance().installEventFilter(detector)
   # Press buttons, then:
   # QApplication.instance().removeEventFilter(detector)

Standard Qt Button Codes
^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Code
     - Qt Constant
     - Typical Button
   * - 1
     - Qt.LeftButton
     - Left click
   * - 2
     - Qt.RightButton
     - Right click
   * - 4
     - Qt.MiddleButton
     - Middle click / wheel
   * - 8
     - Qt.BackButton
     - Back (thumb)
   * - 16
     - Qt.ForwardButton
     - Forward (thumb)
   * - 32
     - Qt.ExtraButton1
     - Additional button
   * - 64
     - Qt.ExtraButton2
     - Additional button
   * - ...
     - Qt.ExtraButton3+
     - Additional buttons

Platform Considerations
-----------------------

Button codes may differ between operating systems for the same physical button.

Windows
^^^^^^^

- Generally consistent with Qt standard codes
- Gaming mice may use extended codes (> 32)

macOS
^^^^^

- Requires accessibility permissions
- Some buttons may be intercepted by the system

Linux
^^^^^

- X11 and Wayland may report different codes
- evdev can provide additional button information

For cross-platform profiles, test on all target platforms or document
platform-specific codes.

Testing Your Profile
--------------------

1. **Load the profile**: Select it from the mouse dropdown

2. **Verify buttons appear**: Check the mapping table shows all buttons

3. **Test each button**: Map each to a distinct action and verify

4. **Test remappable flag**: Ensure non-remappable buttons can't be changed

5. **Test default preset**: Load the default preset and verify mappings

Contributing a Profile
----------------------

To contribute a profile for a popular mouse:

1. Create the mouse definition JSON
2. Create a default preset
3. Test on your platform
4. Submit a pull request with:

   - Mouse definition file
   - Default preset file
   - Update to supported mice table
   - Your platform (for testing reference)

See Also
--------

- :doc:`architecture` - MouseProfile class details
- :doc:`/reference/presets` - Preset format specification
