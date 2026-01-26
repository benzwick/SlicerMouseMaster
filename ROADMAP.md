# SlicerMouseMaster Roadmap

This document tracks the development milestones for SlicerMouseMaster.

## Version Overview

| Version | Milestone | Status |
|---------|-----------|--------|
| v0.1.0 | Foundation | Complete |
| v0.2.0 | Core Event Handling | Complete |
| v0.3.0 | Preset System | Complete |
| v0.4.0 | First Mouse Profiles | Complete |
| v0.5.0 | User Interface | Complete |
| v0.6.0 | Button Auto-Detection | Complete |
| v0.7.0 | Context-Sensitive Bindings | Complete |
| v0.8.0 | Action Library | Complete |
| v0.9.0 | Preset Sharing | Complete |
| v1.0.0 | Production Ready | In Progress |

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
- [x] Create MouseMasterLib/ directory structure
- [x] Create placeholder modules with docstrings
- [x] Create Resources/MouseDefinitions/ structure
- [x] Create presets/builtin/ structure

---

## v0.2.0 - Core Event Handling

**Goal**: Implement mouse button event interception and routing.

### Core Implementation
- [x] EventHandler: Qt application-level event filter
- [x] EventHandler: VTK observer integration
- [x] PlatformAdapter: Windows button normalization
- [x] PlatformAdapter: Linux button normalization
- [x] PlatformAdapter: macOS button normalization

### Testing
- [x] Unit tests for PlatformAdapter
- [x] Unit tests for EventHandler (mocked)
- [ ] Integration test: event capture in Slicer

---

## v0.3.0 - Preset System

**Goal**: Implement preset loading, saving, and management.

### Core Implementation
- [x] PresetManager: JSON schema validation
- [x] PresetManager: Load presets from disk
- [x] PresetManager: Save presets to disk
- [x] PresetManager: Default presets discovery
- [x] PresetManager: User presets directory

### Data Model
- [x] Preset dataclass with validation
- [x] Mapping dataclass with action references
- [x] Version migration support

### Testing
- [x] Unit tests for serialization/deserialization
- [x] Unit tests for schema validation
- [x] Test fixtures for various preset formats

---

## v0.4.0 - First Mouse Profiles

**Goal**: Add support for common mice with built-in profiles.

### Mouse Definitions
- [x] Generic 3-button mouse profile
- [x] Generic 5-button mouse profile
- [x] Logitech MX Master 3S profile
- [x] Logitech MX Master 4 profile

### Core Implementation
- [x] MouseProfile dataclass
- [x] MouseProfile JSON loader
- [x] MouseProfile validation
- [x] Button enumeration

### Default Presets
- [x] default-generic-3-button.json
- [x] default-generic-5-button.json
- [x] default-mx-master-3s.json
- [x] default-mx-master-4.json

---

## v0.5.0 - User Interface

**Goal**: Create the Qt-based user interface for configuration.

### UI Components
- [x] Mouse selector dropdown
- [x] Preset selector with save/load/export/import
- [x] Button mapping table (editable)
- [x] Action selector dropdown
- [x] Context-sensitive bindings toggle
- [x] Status indicator (active/inactive)

### Resources
- [x] Programmatic UI (replaced Qt Designer .ui file)
- [x] MouseMaster.png (module icon)

### Integration
- [x] Connect UI to PresetManager
- [x] Connect UI to EventHandler enable/disable
- [x] Settings persistence on module exit

---

## v0.6.0 - Button Auto-Detection

**Goal**: Allow users to detect button codes for unsupported mice.

### Core Implementation
- [x] ButtonDetector: Interactive detection wizard
- [x] ButtonDetector: Qt event capture mode
- [ ] ButtonDetector: Linux evdev fallback (optional)
- [x] Profile generation from detected buttons

### UI
- [x] Detection wizard dialog
- [x] Button press visualization
- [x] Profile save dialog

---

## v0.7.0 - Context-Sensitive Bindings

**Goal**: Different button mappings per Slicer module.

### Core Implementation
- [x] Module detection (current active module)
- [x] Context override lookup in presets
- [x] Fallback to default mappings

### Module-Specific Defaults
- [x] SegmentEditor context mappings
- [x] Markups context mappings
- [x] VolumeRendering context mappings

### UI
- [x] Context-specific binding editor
- [x] Per-module override toggle

---

## v0.8.0 - Action Library

**Goal**: Comprehensive library of Slicer actions that can be bound.

### Core Implementation
- [x] ActionRegistry: Singleton action registry
- [x] ActionRegistry: Built-in action registration
- [x] ActionRegistry: Custom action registration
- [ ] ActionRegistry: Action discovery from Slicer

### Built-in Actions
- [x] Navigation actions (reset 3D view)
- [x] Edit actions (undo, redo)
- [x] Segment Editor actions (effects, segments)
- [x] View actions (crosshair toggle/center)

### Custom Actions
- [x] Python command execution
- [x] Menu action trigger by name
- [x] Keyboard shortcut simulation

---

## v0.9.0 - Preset Sharing

**Goal**: Enable community preset sharing.

### Core Implementation
- [x] Export preset to JSON file
- [x] Import preset from JSON file
- [x] Preset validation on import

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
- [x] Full unit test coverage (67 tests passing)
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
