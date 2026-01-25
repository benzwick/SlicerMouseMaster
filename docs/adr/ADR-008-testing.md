# ADR-008: Testing Strategy

## Status

Accepted

## Context

Testing a Slicer extension presents unique challenges:
- Some code requires Slicer runtime (VTK, Qt, MRML)
- Event handling tests need actual Qt events
- UI tests require widget instantiation
- CI environments don't have Slicer installed

Testing approaches considered:
1. **All tests in Slicer**: Use Slicer's test framework exclusively
2. **All tests standalone**: Mock everything, run with pytest
3. **Hybrid**: Unit tests standalone, integration tests in Slicer

## Decision

Use a **hybrid testing strategy**:

### Unit Tests (pytest, CI-compatible)

Pure Python tests that don't require Slicer:

```
MouseMaster/Testing/Python/
├── conftest.py           # Fixtures
├── test_mouse_profile.py # Profile dataclass tests
├── test_preset_manager.py # Preset serialization tests
└── test_fixtures/
    ├── valid_preset.json
    └── invalid_preset.json
```

What to test:
- MouseProfile dataclass validation
- Preset serialization/deserialization
- JSON schema validation
- Configuration utilities
- Platform adapter logic (mocked platform)

Run with:
```bash
uv run pytest MouseMaster/Testing/Python/ -v
```

### Integration Tests (Slicer-based)

Tests requiring Slicer runtime:

```python
class MouseMasterTest(ScriptedLoadableModuleTest):
    def test_module_loads(self):
        """Test module can be loaded."""
        self.assertIsNotNone(slicer.modules.mousemaster)

    def test_event_handler_installed(self):
        """Test event handler is installed on app."""
        # Check event filter is active
        pass

    def test_button_mapping_works(self):
        """Test button press triggers mapped action."""
        # Simulate button press, verify action
        pass
```

Run in Slicer:
```python
import MouseMaster
test = MouseMaster.MouseMasterTest()
test.runTest()
```

### Manual Tests (documented procedures)

Complex scenarios documented in `docs/TESTING.md`:

| ID | Test | Procedure |
|----|------|-----------|
| MT-001 | Basic button mapping | 1. Select mouse, 2. Map back button to undo, 3. Press back, 4. Verify undo |
| MT-002 | Preset persistence | 1. Create preset, 2. Restart Slicer, 3. Verify preset loaded |
| MT-003 | Cross-platform | Run MT-001 on Windows, macOS, Linux |

### CI Pipeline

GitHub Actions workflow:
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run mypy MouseMaster/MouseMasterLib/

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: uv run pytest MouseMaster/Testing/Python/ -v
```

## Consequences

### Positive

- Fast unit tests run in CI on every PR
- Integration tests verify actual Slicer behavior
- Manual tests document complex user scenarios
- Clear separation of test types
- Developers can run unit tests without Slicer

### Negative

- Two test frameworks to maintain
- Integration tests require manual trigger
- Some code paths only tested in Slicer

### Neutral

- Need good mocking for unit tests
- Manual tests require documentation discipline

## References

- pytest: https://docs.pytest.org/
- Slicer Testing: https://slicer.readthedocs.io/en/latest/developer_guide/modules/testing.html
- [ADR-001](ADR-001-event-interception.md): Event handler testing considerations
