# ADR-006: UI Framework Choices

## Status

Accepted

## Context

MouseMaster needs a user interface for:
- Selecting mouse model
- Choosing and managing presets
- Editing button mappings
- Configuring context-sensitive bindings
- Running button detection wizard

Slicer extensions can use:
1. **Qt Designer .ui files**: Visual design, loaded at runtime
2. **Programmatic Qt**: Build UI in Python code
3. **ctk widgets**: Slicer's custom widgets (ctkCollapsibleButton, etc.)
4. **qMRML widgets**: MRML-aware widgets for scene data

## Decision

Use **Qt Designer .ui files** as the primary UI definition, supplemented with programmatic Qt for dynamic elements.

### UI Structure

```
MouseMaster.ui
├── qMRMLWidget (top-level, scene connection)
│   ├── ctkCollapsibleButton: "Mouse Selection"
│   │   ├── QComboBox: mouseSelector
│   │   └── QPushButton: detectMouseButton
│   │
│   ├── ctkCollapsibleButton: "Preset"
│   │   ├── QComboBox: presetSelector
│   │   ├── QPushButton: savePresetButton
│   │   ├── QPushButton: exportPresetButton
│   │   └── QPushButton: importPresetButton
│   │
│   ├── ctkCollapsibleButton: "Button Mappings"
│   │   └── QTableWidget: mappingTable
│   │
│   └── ctkCollapsibleButton: "Advanced" (collapsed by default)
│       ├── QCheckBox: contextSensitiveCheckbox
│       └── QTableWidget: contextMappingTable
```

### Design Principles

1. **Collapsible sections**: Use `ctkCollapsibleButton` for organization
2. **Minimal clutter**: Hide advanced options by default
3. **Immediate feedback**: Changes apply immediately (no separate "Apply" button for mappings)
4. **Standard Slicer patterns**: Match other Slicer modules' look and feel

### Dynamic Elements

Some UI elements are built programmatically:
- Action selector dropdowns (populated from ActionRegistry)
- Button detection wizard dialog
- Context-specific mapping rows

## Consequences

### Positive

- Qt Designer provides visual design environment
- .ui files are readable XML (git-friendly)
- Easy to iterate on layout without code changes
- Standard Slicer patterns (ctk) for consistency
- Designers can contribute without Python knowledge

### Negative

- Qt Designer requires separate installation/learning
- Split between .ui and programmatic code can be confusing
- Dynamic elements require Python code anyway

### Neutral

- Need to maintain both .ui file and Python connections
- UI modifications require updating both if widgets change

## References

- Qt Designer: https://doc.qt.io/qt-5/qtdesigner-manual.html
- CTK Widgets: https://commontk.org/
- Slicer Module UI Guide: https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html
