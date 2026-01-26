# Contributing Presets

This guide explains how to create and share button mapping presets for SlicerMouseMaster.

## Preset File Format

Presets are JSON files with the following structure:

```json
{
  "id": "my_workflow_preset",
  "name": "My Workflow Preset",
  "version": "1.0",
  "mouseId": "logitech_mx_master_3s",
  "author": "Your Name",
  "description": "Optimized for segmentation workflows",
  "mappings": {
    "back": {"action": "edit_undo"},
    "forward": {"action": "edit_redo"},
    "middle": {"action": "view_reset_3d"}
  },
  "contextMappings": {
    "SegmentEditor": {
      "back": {"action": "segment_previous"},
      "forward": {"action": "segment_next"}
    }
  }
}
```

### Required Fields

| Field | Description |
|-------|-------------|
| `id` | Unique identifier (lowercase, underscores) |
| `name` | Human-readable name |
| `version` | Preset format version (currently "1.0") |
| `mouseId` | Target mouse profile ID |

### Optional Fields

| Field | Description |
|-------|-------------|
| `author` | Your name or handle |
| `description` | Brief description of the preset's purpose |
| `mappings` | Default button-to-action mappings |
| `contextMappings` | Per-module override mappings |

## Available Actions

### Built-in Actions

| Action ID | Description |
|-----------|-------------|
| `edit_undo` | Undo last action |
| `edit_redo` | Redo last undone action |
| `view_reset_3d` | Reset 3D view orientation |
| `view_center_crosshair` | Center view on crosshair |
| `view_toggle_crosshair` | Toggle crosshair visibility |
| `segment_editor_paint` | Activate Paint effect |
| `segment_editor_erase` | Activate Erase effect |
| `segment_next` | Select next segment |
| `segment_previous` | Select previous segment |
| `markups_place_fiducial` | Start placing fiducial points |
| `markups_delete_point` | Delete last control point |
| `volumerendering_toggle` | Toggle volume rendering |

### Custom Actions

You can also use these action types:

**Python Command:**
```json
{
  "action": "python_command",
  "parameters": {
    "command": "slicer.util.selectModule('SegmentEditor')"
  }
}
```

**Keyboard Shortcut:**
```json
{
  "action": "keyboard_shortcut",
  "parameters": {
    "key": "Z",
    "modifiers": ["ctrl"]
  }
}
```

**Slicer Menu Action:**
```json
{
  "action": "slicer_menu_ActionName",
  "actionId": "ActionName"
}
```

## Mouse Profile IDs

| Mouse | Profile ID |
|-------|------------|
| Generic 3-Button | `generic_3_button` |
| Generic 5-Button | `generic_5_button` |
| Logitech MX Master 3S | `logitech_mx_master_3s` |
| Logitech MX Master 4 | `logitech_mx_master_4` |

## Button IDs

Standard button IDs used in mappings:

| Button ID | Description |
|-----------|-------------|
| `left` | Left click (usually not remappable) |
| `right` | Right click (usually not remappable) |
| `middle` | Middle click / scroll wheel click |
| `back` | Back button (thumb area) |
| `forward` | Forward button (thumb area) |
| `thumb` | Additional thumb button |

## Context Modules

Common Slicer modules for context-sensitive bindings:

- `SegmentEditor` - Segmentation editing
- `Markups` - Fiducial and curve placement
- `VolumeRendering` - 3D volume visualization
- `Models` - Surface model viewing
- `Transforms` - Transform editing

## Creating a Preset

1. **Start with the UI**: Use MouseMaster's button mapping table to configure your bindings
2. **Export**: Use the preset management section to export your preset
3. **Edit metadata**: Add author and description to the JSON file
4. **Test**: Import the preset and verify all bindings work

## Sharing Your Preset

### Option 1: GitHub Issue (Recommended)

1. Go to the [SlicerMouseMaster repository](https://github.com/username/SlicerMouseMaster)
2. Create a new issue with the title: `[Preset] Your Preset Name`
3. Attach your `.json` preset file
4. Include:
   - Target mouse model
   - Workflow description
   - Any special instructions

### Option 2: Pull Request

1. Fork the repository
2. Add your preset to `presets/community/`
3. Update the preset index if one exists
4. Submit a pull request

## Preset Guidelines

When creating presets for sharing:

1. **Use descriptive names**: "Segmentation Workflow" not "my_preset"
2. **Include context mappings**: Make use of module-specific bindings
3. **Document your workflow**: Add a description explaining the intended use
4. **Test thoroughly**: Verify all bindings work in Slicer
5. **Consider ergonomics**: Group related actions on nearby buttons

## Validation

Before sharing, validate your preset:

```python
import json
from pathlib import Path

# Load and validate
with open("my_preset.json") as f:
    data = json.load(f)

required = ["id", "name", "version", "mouseId"]
for field in required:
    assert field in data, f"Missing required field: {field}"

print("Preset is valid!")
```

## Examples

See the built-in presets in `presets/builtin/` for examples:

- `default_generic_3_button.json` - Minimal 3-button setup
- `default_generic_5_button.json` - Standard 5-button with context bindings
- `default_mx_master_3s.json` - Full MX Master 3S configuration
