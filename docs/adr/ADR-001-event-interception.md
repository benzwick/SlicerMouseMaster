# ADR-001: Event Interception Strategy

## Status

Accepted

## Context

SlicerMouseMaster needs to intercept mouse button events before they reach Slicer's default handlers. This allows remapping buttons to custom actions without modifying Slicer's core code.

There are several approaches to intercepting mouse events in a Qt/VTK application like 3D Slicer:

1. **Qt Application Event Filter**: Install a filter at the application level that sees all events
2. **VTK Interactor Observers**: Add observers to VTK render window interactors
3. **Widget-level Event Filters**: Install filters on specific widgets
4. **Subclass Interactor Styles**: Create custom VTK interactor styles

## Decision

We will use a **hybrid approach**:

1. **Primary**: Qt application-level event filter for capturing mouse button presses
2. **Secondary**: VTK observers for render-window-specific events when needed

The Qt event filter is installed on `slicer.app`:
```python
class MouseMasterEventHandler(qt.QObject):
    def eventFilter(self, obj, event):
        if event.type() == qt.QEvent.MouseButtonPress:
            # Handle button press
            return True  # Consume event
        return False  # Pass through
```

VTK observers are added for cases where we need render-window context:
```python
interactor.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self.onPress)
```

## Consequences

### Positive

- Application-level filter catches all mouse events regardless of focused widget
- Single point of interception simplifies the architecture
- VTK observers available for specialized render window handling
- Can consume events (return True) or pass through (return False)
- Works with Slicer's existing event handling without modification

### Negative

- Must be careful not to block essential Slicer functionality
- Order of event filter installation matters for priority
- Need to handle both Qt button codes and VTK button codes
- Testing requires either mocking Qt events or running in Slicer

### Neutral

- Requires understanding of both Qt and VTK event systems
- May need platform-specific handling for certain buttons

## References

- Qt Event System: https://doc.qt.io/qt-5/eventsandfilters.html
- VTK Observers: https://vtk.org/doc/nightly/html/classvtkObject.html
- [ADR-004](ADR-004-platform-differences.md): Platform-specific button handling
