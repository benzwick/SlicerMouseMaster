# ADR-004: Platform Differences

## Status

Accepted

## Context

Mouse button handling differs across Windows, macOS, and Linux:

- **Button codes**: Qt button enums are consistent, but underlying values may differ
- **Modifier keys**: Meta vs. Ctrl key conventions (especially macOS)
- **Extra buttons**: Forward/back button availability and codes
- **Scroll events**: Horizontal scroll, precision scrolling (macOS)
- **Device detection**: How to enumerate connected mice

## Decision

Create a **PlatformAdapter** abstraction that normalizes platform differences:

```python
class PlatformAdapter(ABC):
    @abstractmethod
    def normalize_button(self, qt_button: int) -> str:
        """Convert Qt button code to canonical button ID."""
        pass

    @abstractmethod
    def normalize_modifiers(self, qt_modifiers: int) -> set[str]:
        """Convert Qt modifiers to canonical modifier set."""
        pass

    @staticmethod
    def get_instance() -> "PlatformAdapter":
        if sys.platform == "win32":
            return WindowsAdapter()
        elif sys.platform == "darwin":
            return MacOSAdapter()
        else:
            return LinuxAdapter()
```

### Platform-Specific Implementations

**WindowsAdapter**:
- Standard Qt button codes
- Forward/back buttons at codes 8, 16
- No special handling needed for most cases

**MacOSAdapter**:
- Swap Ctrl/Meta for consistency with Windows/Linux conventions
- Handle precision scroll wheel events
- Forward/back may require special handling

**LinuxAdapter**:
- Standard Qt button codes
- Optional evdev integration for additional buttons
- Handle X11 vs Wayland differences if needed

### Canonical Button IDs

All platforms map to these canonical IDs:
- `left`, `right`, `middle`
- `back`, `forward`
- `extra1`, `extra2`, etc. (for additional buttons)
- `scroll_up`, `scroll_down`, `scroll_left`, `scroll_right`

## Consequences

### Positive

- Single abstraction hides platform complexity
- Presets are portable across platforms
- Easy to add new platform support
- Business logic doesn't need platform checks
- Clear separation of concerns

### Negative

- Requires testing on all platforms
- Some edge cases may not be normalized perfectly
- Additional abstraction layer adds complexity

### Neutral

- Canonical IDs must be documented and stable
- Platform detection happens at startup

## References

- Qt Platform Abstractions: https://doc.qt.io/qt-5/qpa.html
- [ADR-001](ADR-001-event-interception.md): Event interception uses adapter
- [ADR-003](ADR-003-button-detection.md): Button detection with platform awareness
