# ADR-010: Context-Sensitive Bindings

## Status

Accepted

## Context

Different Slicer modules benefit from different button mappings:
- Segment Editor: Effects, segment navigation
- Markups: Placement modes, point editing
- Volume Rendering: View presets, opacity controls
- General: Undo/redo, view navigation

Users should be able to:
- Set default bindings that apply everywhere
- Override specific bindings for specific modules
- Easily see which bindings are active

## Decision

Implement **module-based context detection** with override dictionaries.

### Context Detection

```python
def get_current_context() -> str:
    """Get the currently active Slicer module name."""
    module_manager = slicer.app.moduleManager()
    current = module_manager.currentModule()
    return current if current else "default"
```

### Binding Lookup Order

When a button is pressed:
1. Check `contextMappings[current_module][button_id]`
2. If not found, check `mappings[button_id]`
3. If not found, pass through (don't consume event)

```python
def get_binding(preset: Preset, button_id: str, context: str) -> Mapping | None:
    # Try context-specific first
    if context in preset.context_mappings:
        if button_id in preset.context_mappings[context]:
            return preset.context_mappings[context][button_id]

    # Fall back to default
    if button_id in preset.mappings:
        return preset.mappings[button_id]

    return None
```

### Preset Format

```json
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
      "thumb": {"action": "markup_place_point"}
    }
  }
}
```

### UI Indication

When context-sensitive bindings are active:
- UI shows current context name
- Mapping table shows overridden bindings highlighted
- Tooltip shows "Default" vs "SegmentEditor override"

### Supported Contexts

Initially supported module contexts:
- `SegmentEditor`
- `Markups`
- `VolumeRendering`
- `Models`
- `Transforms`
- `default` (fallback)

Additional modules can be added based on user demand.

## Consequences

### Positive

- Intuitive: bindings adapt to current workflow
- Flexible: users control which modules get overrides
- Discoverable: UI shows current active bindings
- Backwards compatible: presets without contextMappings work fine

### Negative

- More complex preset format
- UI needs to show active context
- Users might be confused if bindings change unexpectedly

### Neutral

- Module names must match exactly (case-sensitive)
- Empty context section means "use defaults"
- Context detection happens on every button press (fast)

## Future Consideration

Could extend context to include:
- Node type (when segmentation node is selected)
- View type (3D vs slice view focus)
- Active tool within module

## References

- Slicer Module Manager: https://slicer.readthedocs.io/en/latest/developer_guide/module_overview.html
- [ADR-009](ADR-009-action-mapping.md): Actions executed based on context
- [ADR-002](ADR-002-preset-file-format.md): Preset format including context mappings
