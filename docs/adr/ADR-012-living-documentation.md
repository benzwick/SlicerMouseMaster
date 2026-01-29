# ADR-012: Living Documentation

## Status

Accepted

## Context

Static documentation becomes stale over time:

- Available actions in ActionRegistry change as new features are added
- Mouse profiles in MouseDefinitions are updated with new devices
- Screenshots may not reflect current UI state
- Manual documentation updates are error-prone and often forgotten

We need a documentation strategy that keeps reference documentation synchronized with the actual code and data.

## Decision

We will generate reference documentation from tests that introspect actual code and data.

### Documentation Generation Pattern

1. **Test introspects source of truth**
   - `test_generate_mouse_profiles.py` reads JSON files from `MouseDefinitions/`
   - `test_generate_actions_reference.py` introspects `ActionRegistry`
   - `test_tutorial_workflow.py` captures screenshots during actual workflows

2. **Test generates RST files**
   - Output goes to `docs/reference/_generated/` or `docs/user-guide/_generated/`
   - Generated files are gitignored (not committed)
   - Static RST files use `.. include::` directives to pull in generated content

3. **CI runs tests → builds docs**
   - GitHub Actions runs generation scripts as part of build
   - Sphinx build includes freshly generated content
   - Documentation artifacts include current generated content

### What Gets Generated

| Source | Generator | Output |
|--------|-----------|--------|
| `MouseDefinitions/*.json` | `test_generate_mouse_profiles.py` | `docs/reference/_generated/mouse-profiles.rst` |
| `ActionRegistry` | `test_generate_actions_reference.py` | `docs/reference/_generated/actions.rst` |
| UI workflow | `test_tutorial_workflow.py` | `docs/user-guide/_generated/*.png` |

### Generator Requirements

- **Mouse Profiles Generator**: Can run standalone (Python only, reads JSON)
- **Actions Generator**: Requires Slicer context (imports ActionRegistry)
- **Tutorial Generator**: Requires Slicer with UI (captures screenshots)

## Consequences

### Positive

- Documentation always matches current code and data
- Tests verify documentation is generatable (catches import errors, missing data)
- Single source of truth (code/data defines behavior AND docs)
- No manual documentation updates for routine changes
- CI catches documentation generation failures

### Negative

- Generated documentation must be excluded from git (requires `.gitignore` update)
- Local development requires running generators to preview docs
- Slicer-dependent generators require full Slicer environment

### Neutral

- Documentation build becomes dependent on test execution
- Some documentation remains static (conceptual guides, tutorials prose)
- Trade-off between flexibility (static docs) and accuracy (generated docs)

## Implementation

1. Create `test_generate_mouse_profiles.py` (standalone Python)
2. Create `test_generate_actions_reference.py` (requires Slicer)
3. Update `docs/reference/` to include generated content
4. Add `docs/reference/_generated/` to `.gitignore`
5. Update CI workflow to run generators before Sphinx build
6. Update existing RST files to use `.. include::` directives

## References

- [ADR-011: Documentation Infrastructure](ADR-011-documentation-infrastructure.md)
- [ADR-008: Testing Strategy](ADR-008-testing.md)
- [Sphinx Include Directive](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-include)
