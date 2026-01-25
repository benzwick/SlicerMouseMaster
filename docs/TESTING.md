# MouseMaster Testing Guide

This document describes the testing strategy and procedures for MouseMaster.

## Testing Overview

MouseMaster uses a hybrid testing approach:

| Test Type | Tool | Environment | When to Run |
|-----------|------|-------------|-------------|
| Unit Tests | pytest | Any Python 3.9+ | On every commit, in CI |
| Integration Tests | Slicer Test Framework | 3D Slicer | Before release |
| Manual Tests | Human | 3D Slicer | Before release, for specific features |

## Unit Tests

### Running Unit Tests

```bash
# Run all unit tests
uv run pytest MouseMaster/Testing/Python/ -v

# Run with coverage
uv run pytest MouseMaster/Testing/Python/ -v --cov=MouseMaster/MouseMasterLib

# Run specific test file
uv run pytest MouseMaster/Testing/Python/test_mouse_profile.py -v

# Run specific test
uv run pytest MouseMaster/Testing/Python/test_mouse_profile.py::TestMouseProfile::test_from_dict -v
```

### What Unit Tests Cover

- `test_mouse_profile.py`: MouseButton, MouseFeatures, MouseProfile classes
- `test_preset_manager.py`: Mapping, Preset, PresetManager classes
- `test_platform_adapter.py`: PlatformAdapter and platform-specific adapters
- `test_button_detector.py`: ButtonDetector and detection session

### Adding New Unit Tests

1. Create test file in `MouseMaster/Testing/Python/test_*.py`
2. Import from `MouseMasterLib`
3. Use fixtures from `conftest.py`
4. Follow naming: `test_<what_is_tested>`

## Integration Tests

### Running in Slicer

```python
# In Slicer Python console
import MouseMaster
test = MouseMaster.MouseMasterTest()
test.runTest()
```

### What Integration Tests Cover

- Module loading and initialization
- Event handler installation
- UI widget creation
- Settings persistence

## Manual Test Procedures

### MT-001: Basic Button Mapping

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

**Expected Result**: Pressing Back triggers undo

**Pass Criteria**: Action undone on button press

---

### MT-002: Preset Save/Load

**Purpose**: Verify presets persist across sessions

**Prerequisites**:
- MouseMaster module loaded

**Steps**:
1. Create a new preset with custom mappings
2. Save the preset
3. Close and reopen 3D Slicer
4. Open MouseMaster module
5. Select the saved preset

**Expected Result**: Preset loads with correct mappings

**Pass Criteria**: All mappings match original configuration

---

### MT-003: Context-Sensitive Bindings

**Purpose**: Verify different bindings in different modules

**Prerequisites**:
- Preset with context-specific mappings

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

**Expected Result**: Different action per module

**Pass Criteria**: Correct action in each module

---

### MT-004: Device Hot-Plug

**Purpose**: Verify behavior when mouse is disconnected/reconnected

**Prerequisites**:
- MouseMaster active with preset

**Steps**:
1. Activate MouseMaster with preset
2. Disconnect mouse USB
3. Wait 5 seconds
4. Reconnect mouse
5. Test button mapping

**Expected Result**: Button mappings work after reconnect

**Pass Criteria**: No crashes, mappings restored

---

### MT-005: Cross-Platform Verification

**Purpose**: Verify functionality on all platforms

**Prerequisites**:
- Access to Windows, macOS, and Linux systems

**Steps** (repeat on each platform):
1. Install extension
2. Load module
3. Run MT-001 basic mapping test
4. Run MT-002 preset save/load test
5. Check Slicer console for errors

**Expected Result**: All tests pass on all platforms

**Pass Criteria**: No platform-specific failures

---

### MT-006: Button Detection Wizard

**Purpose**: Verify button detection for new mice

**Prerequisites**:
- Mouse not in built-in profiles

**Steps**:
1. Open MouseMaster
2. Click "Detect New Mouse..."
3. Follow prompts to press each button
4. Name the profile
5. Click Done
6. Verify profile appears in dropdown
7. Create mappings and test

**Expected Result**: Custom profile created and usable

**Pass Criteria**: Profile saved, buttons mappable

---

### MT-007: Preset Export/Import

**Purpose**: Verify preset sharing functionality

**Prerequisites**:
- Existing preset with mappings

**Steps**:
1. Select preset
2. Click "Export..."
3. Save to file
4. Delete the preset (or use different Slicer install)
5. Click "Import..."
6. Select the exported file
7. Verify preset imported correctly

**Expected Result**: Preset exported and imported successfully

**Pass Criteria**: Imported preset matches original

---

### MT-008: Error Handling

**Purpose**: Verify graceful error handling

**Prerequisites**:
- MouseMaster module

**Steps**:
1. Try to load corrupt preset JSON
2. Try to import nonexistent file
3. Try to save preset without mouse selected
4. Check Slicer console for error messages

**Expected Result**: User-friendly error messages, no crashes

**Pass Criteria**: Errors logged, UI remains responsive

---

## CI/CD Pipeline

The GitHub Actions workflow runs:

```yaml
jobs:
  lint:
    - ruff check .
    - ruff format --check .
    - mypy MouseMaster/MouseMasterLib/

  test:
    - pytest MouseMaster/Testing/Python/ -v
```

## Test Matrix

| Feature | Unit | Integration | Manual |
|---------|------|-------------|--------|
| MouseProfile parsing | X | | |
| Preset serialization | X | | |
| Platform adaptation | X | | |
| Button detection | X | | MT-006 |
| Event handling | | X | MT-001 |
| UI functionality | | X | MT-001-008 |
| Persistence | | X | MT-002 |
| Context bindings | | | MT-003 |
| Cross-platform | | | MT-005 |

## Reporting Issues

When reporting test failures:

1. Note which test failed (ID if manual)
2. Include Slicer version
3. Include OS and version
4. Attach Slicer console output
5. Attach MouseMaster log if available
