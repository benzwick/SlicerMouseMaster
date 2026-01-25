# SlicerMouseMaster Roadmap

This document tracks the development milestones for SlicerMouseMaster.

## Version Overview

| Version | Milestone | Status |
|---------|-----------|--------|
| v0.1.0 | Foundation | In Progress |
| v0.2.0 | Core Event Handling | Planned |
| v0.3.0 | Preset System | Planned |
| v0.4.0 | First Mouse Profiles | Planned |
| v0.5.0 | User Interface | Planned |
| v0.6.0 | Button Auto-Detection | Planned |
| v0.7.0 | Context-Sensitive Bindings | Planned |
| v0.8.0 | Action Library | Planned |
| v0.9.0 | Preset Sharing | Planned |
| v1.0.0 | Production Ready | Planned |

---

## v0.1.0 - Foundation

**Goal**: Establish project structure, documentation, and development infrastructure.

### Documentation
- [x] Create CLAUDE.md (developer reference)
- [x] Create README.md (user documentation)
- [x] Create ROADMAP.md (this file)
- [x] Create docs/adr/README.md (ADR template and index)
- [x] Create ADR-001 through ADR-010

### Project Setup
- [x] Create pyproject.toml
- [x] Create .pre-commit-config.yaml
- [x] Create .env.example
- [x] Create .claude/skills/ for workflow automation

### Structure
- [ ] Create MouseMasterLib/ directory structure
- [ ] Create placeholder modules with docstrings
- [ ] Create Resources/MouseDefinitions/ structure
- [ ] Create presets/builtin/ structure

---

## v0.2.0 - Core Event Handling

**Goal**: Implement mouse button event interception and routing.

### Core Implementation
- [ ] EventHandler: Qt application-level event filter
- [ ] EventHandler: VTK observer integration
- [ ] PlatformAdapter: Windows button normalization
- [ ] PlatformAdapter: Linux button normalization
- [ ] PlatformAdapter: macOS button normalization

### Testing
- [ ] Unit tests for PlatformAdapter
- [ ] Unit tests for EventHandler (mocked)
- [ ] Integration test: event capture in Slicer

---

## v0.3.0 - Preset System

**Goal**: Implement preset loading, saving, and management.

### Core Implementation
- [ ] PresetManager: JSON schema validation
- [ ] PresetManager: Load presets from disk
- [ ] PresetManager: Save presets to disk
- [ ] PresetManager: Default presets discovery
- [ ] PresetManager: User presets directory

### Data Model
- [ ] Preset dataclass with validation
- [ ] Mapping dataclass with action references
- [ ] Version migration support

### Testing
- [ ] Unit tests for serialization/deserialization
- [ ] Unit tests for schema validation
- [ ] Test fixtures for various preset formats

---

## v0.4.0 - First Mouse Profiles

**Goal**: Add support for common mice with built-in profiles.

### Mouse Definitions
- [ ] Generic 3-button mouse profile
- [ ] Generic 5-button mouse profile
- [ ] Logitech MX Master 3S profile
- [ ] Logitech MX Master 4 profile

### Core Implementation
- [ ] MouseProfile dataclass
- [ ] MouseProfile JSON loader
- [ ] MouseProfile validation
- [ ] Button enumeration

### Default Presets
- [ ] default-generic-3.json
- [ ] default-generic-5.json
- [ ] default-mx-master-3s.json
- [ ] default-mx-master-4.json

---

## v0.5.0 - User Interface

**Goal**: Create the Qt-based user interface for configuration.

### UI Components
- [ ] Mouse selector dropdown
- [ ] Preset selector with save/load/export/import
- [ ] Button mapping table (editable)
- [ ] Action selector dropdown
- [ ] Context-sensitive bindings toggle
- [ ] Status indicator (active/inactive)

### Resources
- [ ] MouseMaster.ui (Qt Designer)
- [ ] MouseMaster.png (module icon)

### Integration
- [ ] Connect UI to PresetManager
- [ ] Connect UI to EventHandler enable/disable
- [ ] Settings persistence on module exit

---

## v0.6.0 - Button Auto-Detection

**Goal**: Allow users to detect button codes for unsupported mice.

### Core Implementation
- [ ] ButtonDetector: Interactive detection wizard
- [ ] ButtonDetector: Qt event capture mode
- [ ] ButtonDetector: Linux evdev fallback (optional)
- [ ] Profile generation from detected buttons

### UI
- [ ] Detection wizard dialog
- [ ] Button press visualization
- [ ] Profile save dialog

---

## v0.7.0 - Context-Sensitive Bindings

**Goal**: Different button mappings per Slicer module.

### Core Implementation
- [ ] Module detection (current active module)
- [ ] Context override lookup in presets
- [ ] Fallback to default mappings

### Module-Specific Defaults
- [ ] SegmentEditor context mappings
- [ ] Markups context mappings
- [ ] VolumeRendering context mappings

### UI
- [ ] Context-specific binding editor
- [ ] Per-module override toggle

---

## v0.8.0 - Action Library

**Goal**: Comprehensive library of Slicer actions that can be bound.

### Core Implementation
- [ ] ActionRegistry: Singleton action registry
- [ ] ActionRegistry: Built-in action registration
- [ ] ActionRegistry: Custom action registration
- [ ] ActionRegistry: Action discovery from Slicer

### Built-in Actions
- [ ] Navigation actions (zoom, pan, rotate, reset)
- [ ] Edit actions (undo, redo, delete)
- [ ] Segment Editor actions (effects, segments)
- [ ] View actions (crosshair, layout changes)

### Custom Actions
- [ ] Python command execution
- [ ] Menu action trigger by name
- [ ] Keyboard shortcut simulation

---

## v0.9.0 - Preset Sharing

**Goal**: Enable community preset sharing.

### Core Implementation
- [ ] Export preset to JSON file
- [ ] Import preset from JSON file
- [ ] Preset validation on import

### Documentation
- [ ] Preset contribution guide
- [ ] Community preset repository setup
- [ ] GitHub Discussions category for presets

---

## v1.0.0 - Production Ready

**Goal**: Complete documentation, testing, and Extension Index submission.

### Documentation
- [ ] Complete user guide with screenshots
- [ ] Video tutorial
- [ ] FAQ section

### Testing
- [ ] Full unit test coverage (>80%)
- [ ] All manual tests documented and passing
- [ ] Cross-platform verification (Windows, macOS, Linux)

### Release
- [ ] Extension Index submission
- [ ] Release notes
- [ ] Announcement on Slicer Discourse

---

## Future Considerations (Post-1.0)

These features are under consideration for future releases:

- **Gesture Support**: Swipe and multi-finger gestures
- **Macro Recording**: Record and replay action sequences
- **Cloud Sync**: Sync presets across machines
- **Profile Auto-Switch**: Detect connected mouse and switch automatically
- **Haptic Feedback**: For mice that support it
- **Integration with Logitech Options+**: Import settings from vendor software
