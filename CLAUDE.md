# SlicerMouseMaster Developer Guide

## Project Overview

SlicerMouseMaster is a 3D Slicer extension providing advanced mouse customization:
- Button remapping for multi-button mice
- Mouse-specific presets (MX Master 3S/4, generic 3/5 button)
- Context-sensitive bindings per Slicer module
- Preset sharing via JSON export/import
- Auto-detection of button codes

## Pre-commit Hooks (REQUIRED)

**Before making any commits, ensure pre-commit hooks are installed:**

```bash
# Check if hooks are installed
ls -la .git/hooks/pre-commit

# Install hooks (MUST do this before committing)
uv run pre-commit install

# Run hooks manually on all files
uv run pre-commit run --all-files
```

**IMPORTANT:** Never commit without hooks active. If `.git/hooks/pre-commit` doesn't exist or is a sample file, run `uv run pre-commit install` first.

## Quick Commands

```bash
# Run unit tests (outside Slicer)
uv run pytest MouseMaster/Testing/Python/ -v

# Lint and format (hooks run these automatically)
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy MouseMaster/MouseMasterLib/
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

## Living Documentation

Documentation is generated from tests, not written statically:

```bash
# Run tutorial test to generate docs with current screenshots
Slicer --python-script MouseMaster/Testing/Python/test_tutorial_workflow.py

# Output: docs/user-guide/_generated/ (screenshots + tutorial.rst)
```

**Why?**
- Screenshots always match current UI
- Tutorials are verified working code
- Documentation stays in sync with implementation
- CI catches broken tutorials

## Key Paths

| Path | Contents |
|------|----------|
| `MouseMaster/MouseMaster.py` | Module, Widget, Logic classes |
| `MouseMaster/MouseMasterLib/` | EventHandler, PresetManager, ActionRegistry, PlatformAdapter |
| `MouseMaster/Resources/MouseDefinitions/` | Mouse profile JSON files |
| `MouseMaster/Resources/Presets/` | Preset configuration files |
| `docs/` | Sphinx documentation |
| `docs/adr/` | Architecture Decision Records |

## Commit Message Format

```
<type>: <short summary>

[optional body]
[optional footer]
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Troubleshooting

**Button Not Detected**: Check platform adapter logs, try `/detect-buttons` skill, verify mouse is recognized by OS.

**Preset Not Loading**: Validate JSON syntax, check preset version compatibility, verify mouseId matches loaded profile.

**Event Handler Not Active**: Check `slicer.modules.mousemaster` is loaded, verify event filter installed in Slicer console, reload with `slicer.util.reloadScriptedModule('MouseMaster')`.

## Documentation

- [Architecture](docs/developer-guide/architecture.rst) - System design and event flow
- [Data Formats](docs/reference/presets.rst) - Mouse definitions and preset JSON schemas
- [Qt Events](docs/reference/events.rst) - Button constants and modifiers
- [Slicer API](docs/reference/slicer-api.rst) - Common API patterns
- [ADRs](docs/adr/) - Architecture Decision Records
- [Testing](docs/TESTING.md) - Manual test procedures
