# ADR-005: Persistence Strategy

## Status

Accepted

## Context

MouseMaster needs to persist several types of data:

1. **User preferences**: Active mouse, active preset, UI state
2. **User presets**: Custom button mappings created by user
3. **Mouse profiles**: Custom mouse definitions from button detection
4. **Import history**: Record of imported presets

Storage options considered:
1. **Qt Settings** (`QSettings`): Slicer's standard settings mechanism
2. **User directory files**: JSON files in user-specific directory
3. **Slicer scene**: Persist in MRML scene (resets on new scene)
4. **Database**: SQLite or similar (overkill for this use case)

## Decision

Use a **hybrid approach**:

### Qt Settings for Preferences

Small, simple settings stored in Slicer's settings:
```python
settings = qt.QSettings()
settings.setValue("MouseMaster/ActiveMouse", mouse_id)
settings.setValue("MouseMaster/ActivePreset", preset_id)
settings.setValue("MouseMaster/Enabled", True)
```

### User Directory for Presets and Profiles

Larger, structured data stored as JSON files:
```
~/.slicer/MouseMaster/
├── presets/
│   ├── my_custom_preset.json
│   └── imported_preset.json
├── profiles/
│   └── my_detected_mouse.json
└── cache/
    └── action_registry.json
```

Location determined by:
```python
import slicer
user_dir = os.path.join(
    slicer.app.slicerHome,
    "..",
    "MouseMaster"
)
# Or use: slicer.app.slicerUserSettingsFilePath parent directory
```

### Built-in Resources

Default profiles and presets bundled with extension:
```
MouseMaster/
├── Resources/
│   └── MouseDefinitions/
│       ├── logitech_mx_master_3s.json
│       └── generic_3_button.json
└── presets/
    └── builtin/
        └── default_mx_master_3s.json
```

## Consequences

### Positive

- Qt Settings integrates with Slicer's settings management
- File-based presets are easy to backup and share
- Clear separation between user data and extension resources
- Human-readable JSON files for debugging
- Survives Slicer upgrades (user directory persists)

### Negative

- Two storage mechanisms to maintain
- Need to handle migration if file structure changes
- File permissions issues possible on some systems

### Neutral

- User must have write access to user directory
- Built-in resources are read-only

## References

- Qt Settings: https://doc.qt.io/qt-5/qsettings.html
- Slicer Settings: https://slicer.readthedocs.io/en/latest/developer_guide/settings.html
- [ADR-002](ADR-002-preset-file-format.md): Preset file format
- [ADR-007](ADR-007-preset-sharing.md): Preset sharing
