# ADR-009: Slicer Action Mapping

## Status

Accepted

## Context

MouseMaster needs to map button presses to Slicer actions. Actions can include:
- Built-in Slicer commands (undo, redo, save)
- Module-specific actions (Segment Editor effects)
- View manipulation (zoom, pan, rotate)
- Custom Python commands

Need to decide:
- How to discover available actions
- How to represent actions in presets
- How to execute actions when buttons are pressed

## Decision

Implement an **ActionRegistry** pattern with categorized actions.

### ActionRegistry Singleton

```python
class ActionRegistry:
    _instance = None

    @classmethod
    def get_instance(cls) -> "ActionRegistry":
        if cls._instance is None:
            cls._instance = ActionRegistry()
            cls._instance._register_builtin_actions()
        return cls._instance

    def register(
        self,
        action_id: str,
        handler: ActionHandler,
        category: str,
        description: str
    ) -> None:
        self._actions[action_id] = ActionEntry(
            id=action_id,
            handler=handler,
            category=category,
            description=description
        )

    def execute(self, action_id: str, context: ActionContext) -> bool:
        if action_id not in self._actions:
            return False
        return self._actions[action_id].handler.execute(context)
```

### Action Handler Protocol

```python
class ActionHandler(Protocol):
    def execute(self, context: ActionContext) -> bool:
        """Execute the action. Return True if successful."""
        ...

    def is_available(self, context: ActionContext) -> bool:
        """Check if action is currently available."""
        ...
```

### Built-in Action Categories

**Navigation:**
- `view_reset_3d`: Reset 3D view
- `view_zoom_in`, `view_zoom_out`: Zoom controls
- `view_center_crosshair`: Center on crosshair

**Editing:**
- `edit_undo`, `edit_redo`: Undo/redo
- `edit_delete`: Delete selected

**Segment Editor:**
- `segment_editor_paint`, `segment_editor_erase`: Toggle effects
- `segment_next`, `segment_previous`: Navigate segments
- `segment_toggle_visibility`: Show/hide current segment

**Custom:**
- `python_command`: Execute arbitrary Python
- `menu_action`: Trigger menu action by name
- `keyboard_shortcut`: Simulate key press

### Preset Action Reference

```json
{
  "mappings": {
    "back": {
      "action": "edit_undo"
    },
    "forward": {
      "action": "python_command",
      "command": "slicer.util.selectModule('SegmentEditor')"
    },
    "thumb": {
      "action": "menu_action",
      "menuPath": "Edit/Undo"
    }
  }
}
```

## Consequences

### Positive

- Registry pattern allows extension by other modules
- Categorized actions help UI organization
- ActionHandler protocol enables custom implementations
- is_available allows disabling unavailable actions
- Presets reference actions by stable ID

### Negative

- Discovering all Slicer actions is complex
- Some actions are module-specific and may not be available
- Custom Python commands are a security consideration

### Neutral

- Actions can be registered dynamically
- Need to handle action not found gracefully

## References

- Slicer Python API: https://slicer.readthedocs.io/en/latest/developer_guide/python_api.html
- [ADR-010](ADR-010-context-bindings.md): Context affects action availability
- [ADR-002](ADR-002-preset-file-format.md): How actions are referenced in presets
