# ADR-003: Button Detection Mechanism

## Status

Accepted

## Context

Different mice have different button configurations, and button codes can vary by:
- Mouse model
- Operating system
- Driver software (e.g., Logitech Options)

To support arbitrary mice, we need a way to detect which button codes correspond to which physical buttons on a user's mouse.

Detection approaches considered:
1. **Qt Event Capture**: Use Qt's event system to capture button codes
2. **Linux evdev**: Read raw input events on Linux
3. **Windows Raw Input**: Use Windows Raw Input API
4. **USB HID Parsing**: Parse HID descriptors

## Decision

Use **Qt event capture as the primary mechanism** with Linux evdev as an optional enhancement.

### Primary: Qt Event Capture

```python
class ButtonDetectionDialog(qt.QDialog):
    def eventFilter(self, obj, event):
        if event.type() == qt.QEvent.MouseButtonPress:
            button_code = int(event.button())
            self.recordButton(button_code)
            return True
        return False
```

The detection wizard:
1. Displays "Press button X" prompts
2. Captures the Qt button code for each press
3. Records the mapping (physical button → Qt code)
4. Generates a mouse profile JSON

### Secondary: Linux evdev (Optional)

For advanced detection on Linux, optionally use python-evdev:
```python
from evdev import InputDevice, categorize, ecodes
device = InputDevice('/dev/input/eventX')
for event in device.read_loop():
    if event.type == ecodes.EV_KEY:
        print(f"Button: {event.code}")
```

This is optional because:
- Requires additional dependency
- Requires user to be in `input` group
- Qt detection works for most cases

## Consequences

### Positive

- Qt detection works cross-platform without dependencies
- Captures actual button codes as seen by Slicer
- Interactive wizard is user-friendly
- Optional evdev provides fallback for edge cases
- No need to maintain database of all mice

### Negative

- Some buttons might not generate Qt events (gesture buttons)
- evdev requires elevated permissions on Linux
- Cannot detect buttons that are intercepted by driver software

### Neutral

- Users must manually trigger detection wizard
- Detection results are cached in mouse profile

## References

- Qt Mouse Events: https://doc.qt.io/qt-5/qmouseevent.html
- python-evdev: https://python-evdev.readthedocs.io/
- [ADR-004](ADR-004-platform-differences.md): Platform-specific handling
