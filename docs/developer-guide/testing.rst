Testing
=======

This document describes the testing strategy and procedures for MouseMaster.

Testing Overview
----------------

MouseMaster uses a hybrid testing approach:

.. list-table::
   :header-rows: 1

   * - Test Type
     - Tool
     - Environment
     - When to Run
   * - Unit Tests
     - pytest
     - Any Python 3.9+
     - On every commit, in CI
   * - Integration Tests
     - Slicer Test Framework
     - 3D Slicer
     - Before release
   * - Manual Tests
     - Human
     - 3D Slicer
     - Before release

Unit Tests
----------

Running Unit Tests
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Run all unit tests
   uv run pytest MouseMaster/Testing/Python/ -v

   # Run with coverage
   uv run pytest MouseMaster/Testing/Python/ -v --cov=MouseMaster/MouseMasterLib

   # Run specific test file
   uv run pytest MouseMaster/Testing/Python/test_mouse_profile.py -v

   # Run specific test
   uv run pytest MouseMaster/Testing/Python/test_mouse_profile.py::TestMouseProfile::test_from_dict -v

What Unit Tests Cover
^^^^^^^^^^^^^^^^^^^^^

- ``test_mouse_profile.py``: MouseButton, MouseFeatures, MouseProfile classes
- ``test_preset_manager.py``: Mapping, Preset, PresetManager classes
- ``test_platform_adapter.py``: PlatformAdapter and platform-specific adapters
- ``test_button_detector.py``: ButtonDetector and detection session

Adding New Unit Tests
^^^^^^^^^^^^^^^^^^^^^

1. Create test file in ``MouseMaster/Testing/Python/test_*.py``
2. Import from ``MouseMasterLib``
3. Use fixtures from ``conftest.py``
4. Follow naming: ``test_<what_is_tested>``

Example:

.. code-block:: python

   import pytest
   from MouseMasterLib.MouseProfile import MouseProfile

   class TestMouseProfile:
       def test_from_dict_valid(self, sample_mouse_dict):
           profile = MouseProfile.from_dict(sample_mouse_dict)
           assert profile.id == sample_mouse_dict["id"]
           assert len(profile.buttons) == len(sample_mouse_dict["buttons"])

       def test_from_dict_missing_required(self):
           with pytest.raises(KeyError):
               MouseProfile.from_dict({})

Integration Tests
-----------------

Running in Slicer
^^^^^^^^^^^^^^^^^

.. code-block:: python

   # In Slicer Python console
   import MouseMaster
   test = MouseMaster.MouseMasterTest()
   test.runTest()

What Integration Tests Cover
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Module loading and initialization
- Event handler installation
- UI widget creation
- Settings persistence

Manual Test Procedures
----------------------

MT-001: Basic Button Mapping
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Verify button presses trigger mapped actions

**Prerequisites**:

- 3D Slicer running
- MouseMaster module loaded
- Multi-button mouse connected

**Steps**:

1. Open MouseMaster module
2. Select your mouse model from dropdown
3. Select a preset or create new one
4. Map "Back" button to "Undo"
5. Create some action in Slicer (e.g., add a markup point)
6. Press the Back button on your mouse
7. Verify the action was undone

**Pass Criteria**: Action undone on button press

MT-002: Preset Save/Load
^^^^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Verify presets persist across sessions

**Steps**:

1. Create a new preset with custom mappings
2. Save the preset
3. Close and reopen 3D Slicer
4. Open MouseMaster module
5. Select the saved preset

**Pass Criteria**: All mappings match original configuration

MT-003: Context-Sensitive Bindings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Verify different bindings in different modules

**Steps**:

1. Create preset with:

   - Default: Back -> Undo
   - SegmentEditor: Back -> Previous Segment

2. Save preset
3. Open Welcome module, press Back
4. Verify Undo triggered
5. Open Segment Editor, create segmentation
6. Press Back
7. Verify segment selection changed

**Pass Criteria**: Correct action in each module

MT-004: Device Hot-Plug
^^^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Verify behavior when mouse is disconnected/reconnected

**Steps**:

1. Activate MouseMaster with preset
2. Disconnect mouse USB
3. Wait 5 seconds
4. Reconnect mouse
5. Test button mapping

**Pass Criteria**: No crashes, mappings restored

MT-005: Cross-Platform Verification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Verify functionality on all platforms

**Steps** (repeat on each platform):

1. Install extension
2. Load module
3. Run MT-001 basic mapping test
4. Run MT-002 preset save/load test
5. Check Slicer console for errors

**Pass Criteria**: No platform-specific failures

MT-006: Button Detection Wizard
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Verify button detection for new mice

**Steps**:

1. Open MouseMaster
2. Click "Detect New Mouse..."
3. Follow prompts to press each button
4. Name the profile
5. Click Done
6. Verify profile appears in dropdown
7. Create mappings and test

**Pass Criteria**: Profile saved, buttons mappable

MT-007: Preset Export/Import
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Verify preset sharing functionality

**Steps**:

1. Select preset
2. Click "Export..."
3. Save to file
4. Delete the preset (or use different Slicer install)
5. Click "Import..."
6. Select the exported file
7. Verify preset imported correctly

**Pass Criteria**: Imported preset matches original

MT-008: Error Handling
^^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Verify graceful error handling

**Steps**:

1. Try to load corrupt preset JSON
2. Try to import nonexistent file
3. Try to save preset without mouse selected
4. Check Slicer console for error messages

**Pass Criteria**: Errors logged, UI remains responsive

Test Matrix
-----------

.. list-table::
   :header-rows: 1

   * - Feature
     - Unit
     - Integration
     - Manual
   * - MouseProfile parsing
     - X
     -
     -
   * - Preset serialization
     - X
     -
     -
   * - Platform adaptation
     - X
     -
     -
   * - Button detection
     - X
     -
     - MT-006
   * - Event handling
     -
     - X
     - MT-001
   * - UI functionality
     -
     - X
     - MT-001-008
   * - Persistence
     -
     - X
     - MT-002
   * - Context bindings
     -
     -
     - MT-003
   * - Cross-platform
     -
     -
     - MT-005

CI/CD Pipeline
--------------

The GitHub Actions workflow runs:

.. code-block:: yaml

   jobs:
     lint:
       - ruff check .
       - ruff format --check .
       - mypy MouseMaster/MouseMasterLib/

     test:
       - pytest MouseMaster/Testing/Python/ -v

Reporting Issues
----------------

When reporting test failures:

1. Note which test failed (ID if manual)
2. Include Slicer version
3. Include OS and version
4. Attach Slicer console output
5. Attach MouseMaster log if available
