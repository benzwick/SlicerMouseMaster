# SlicerMouseMaster Developer Guide

## Project Overview

SlicerMouseMaster is a 3D Slicer extension providing advanced mouse customization:
- Button remapping for multi-button mice
- Mouse-specific presets (MX Master 3S/4, generic 3/5 button)
- Context-sensitive bindings per Slicer module
- Preset sharing via JSON export/import
- Auto-detection of button codes

## Quick Commands

```bash
# Run unit tests (outside Slicer)
uv run pytest MouseMaster/Testing/Python/ -v

# Lint and format
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy MouseMaster/MouseMasterLib/

# Install pre-commit hooks
uv run pre-commit install

# Run all pre-commit checks
uv run pre-commit run --all-files
```

## Testing in Slicer

```python
# In Slicer Python console
import MouseMaster
slicer.util.reloadScriptedModule('MouseMaster')

# Run Slicer integration tests
test = MouseMaster.MouseMasterTest()
test.runTest()
```

---

## Architecture

```
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
```

### Event Flow

```
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
```

---

## Key Classes

### MouseMaster/MouseMaster.py
- **MouseMaster** - Slicer module registration, metadata
- **MouseMasterWidget** - Qt widget, UI setup, user interaction
- **MouseMasterLogic** - Business logic coordinator

### MouseMaster/MouseMasterLib/

| Class | Responsibility |
|-------|----------------|
| `EventHandler` | Qt event filter, intercepts mouse buttons |
| `MouseProfile` | Dataclass for mouse definition |
| `PresetManager` | Load/save/export/import presets |
| `ActionRegistry` | Singleton registry of Slicer actions |
| `PlatformAdapter` | Cross-platform button code normalization |
| `ButtonDetector` | Auto-detect button codes interactively |

---

## Data Formats

### Mouse Definition (Resources/MouseDefinitions/*.json)

```json
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
```

### Preset Format (presets/*.json)

```json
{
  "id": "segmentation_workflow",
  "name": "Segmentation Workflow",
  "version": "1.0",
  "mouseId": "logitech_mx_master_3s",
  "mappings": {
    "back": {"action": "slicer_action", "actionId": "undo"},
    "forward": {"action": "slicer_action", "actionId": "redo"},
    "thumb": {"action": "segment_editor_effect", "effectName": "Paint"}
  },
  "contextMappings": {
    "SegmentEditor": {
      "back": {"action": "segment_previous"},
      "forward": {"action": "segment_next"}
    }
  }
}
```

---

## Development Guidelines

### Adding a New Mouse Profile

1. Create JSON in `Resources/MouseDefinitions/`:
   ```json
   {
     "id": "vendor_model",
     "name": "Vendor Model Name",
     "buttons": [...]
   }
   ```

2. Add to supported mice table in README.md

3. Create default preset in `presets/builtin/`

4. Test with `/detect-buttons` skill

### Adding a New Action

1. Register in `ActionRegistry.register()`:
   ```python
   registry.register(
       "my_action",
       MyActionHandler(),
       category="custom",
       description="Does something"
   )
   ```

2. Add to action documentation table

### Platform-Specific Code

Use `PlatformAdapter` for cross-platform compatibility:
```python
adapter = PlatformAdapter.get_instance()
normalized_button = adapter.normalize_button(qt_button)
```

Never use platform checks directly in business logic.

---

## VTK Event Reference

| Qt Button | Constant | Typical Mapping |
|-----------|----------|-----------------|
| 1 | Qt.LeftButton | Primary |
| 2 | Qt.RightButton | Context menu |
| 4 | Qt.MiddleButton | Pan/rotate |
| 8 | Qt.BackButton | Back/undo |
| 16 | Qt.ForwardButton | Forward/redo |
| 32 | Qt.ExtraButton1 | Custom (thumb) |

### Modifier Keys

| Qt Modifier | Constant |
|-------------|----------|
| Shift | Qt.ShiftModifier |
| Ctrl | Qt.ControlModifier |
| Alt | Qt.AltModifier |
| Meta | Qt.MetaModifier |

---

## Slicer API Quick Reference

### Get Current Module
```python
current = slicer.app.moduleManager().currentModule()
```

### Trigger Menu Action
```python
mainWindow = slicer.util.mainWindow()
action = mainWindow.findChild(qt.QAction, "actionName")
action.trigger()
```

### Access Segment Editor
```python
editor = slicer.modules.SegmentEditorWidget.editor
editor.setActiveEffectByName("Paint")
```

### Settings Persistence
```python
settings = qt.QSettings()
settings.setValue("MouseMaster/Key", value)
value = settings.value("MouseMaster/Key", default)
```

---

## Commit Message Format

```
<type>: <short summary>

[optional body with details]

[optional footer with references]
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

Examples:
```
feat: add MX Master 4 support

- Add mouse definition JSON
- Create default preset
- Update supported mice documentation

Closes #42
```

---

## ADR Index

| ADR | Title | Status |
|-----|-------|--------|
| [001](docs/adr/ADR-001-event-interception.md) | Event Interception Strategy | Accepted |
| [002](docs/adr/ADR-002-preset-file-format.md) | Preset File Format | Accepted |
| [003](docs/adr/ADR-003-button-detection.md) | Button Detection Mechanism | Accepted |
| [004](docs/adr/ADR-004-platform-differences.md) | Platform Differences | Accepted |
| [005](docs/adr/ADR-005-persistence.md) | Persistence Strategy | Accepted |
| [006](docs/adr/ADR-006-ui-framework.md) | UI Framework Choices | Accepted |
| [007](docs/adr/ADR-007-preset-sharing.md) | Preset Sharing Mechanism | Accepted |
| [008](docs/adr/ADR-008-testing.md) | Testing Strategy | Accepted |
| [009](docs/adr/ADR-009-action-mapping.md) | Slicer Action Mapping | Accepted |
| [010](docs/adr/ADR-010-context-bindings.md) | Context-Sensitive Bindings | Accepted |

---

## Manual Testing

See [docs/TESTING.md](docs/TESTING.md) for manual test procedures.

| ID | Test | Modules Affected |
|----|------|------------------|
| MT-001 | Basic button mapping | All |
| MT-002 | Preset save/load | Presets |
| MT-003 | Context-sensitive bindings | Module-specific |
| MT-004 | Device hot-plug | Platform |
| MT-005 | Cross-platform verification | All |

---

## Troubleshooting

### Button Not Detected
1. Check platform adapter logs
2. Try `/detect-buttons` skill
3. Verify mouse is recognized by OS

### Preset Not Loading
1. Validate JSON syntax
2. Check preset version compatibility
3. Verify mouseId matches loaded profile

### Event Handler Not Active
1. Check module is loaded: `slicer.modules.mousemaster`
2. Verify event filter installed: check Slicer console for init messages
3. Reload module: `slicer.util.reloadScriptedModule('MouseMaster')`
