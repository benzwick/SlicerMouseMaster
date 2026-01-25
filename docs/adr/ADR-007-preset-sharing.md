# ADR-007: Preset Sharing Mechanism

## Status

Accepted

## Context

Users should be able to share their button mapping configurations with others. Sharing mechanisms considered:

1. **JSON file export/import**: Simple file-based sharing
2. **GitHub repository**: Curated collection of community presets
3. **Cloud service**: Dedicated preset hosting service
4. **Slicer Extension Manager**: Bundle presets with extension updates
5. **In-app marketplace**: Built-in preset browser

## Decision

Use a **two-tier approach**:

### Primary: JSON Export/Import

Simple file-based sharing as the primary mechanism:

**Export:**
```python
def export_preset(preset: Preset, path: str) -> None:
    with open(path, "w") as f:
        json.dump(preset.to_dict(), f, indent=2)
```

**Import:**
```python
def import_preset(path: str) -> Preset:
    with open(path) as f:
        data = json.load(f)
    validate_preset_schema(data)
    return Preset.from_dict(data)
```

Users can share via:
- Email attachment
- File sharing services (Dropbox, Google Drive)
- Forum posts
- Direct file transfer

### Secondary: GitHub Discussions

Community preset repository using GitHub Discussions:

1. Create "Presets" category in GitHub Discussions
2. Users create discussion posts with:
   - Preset JSON file attached
   - Mouse model
   - Workflow description
   - Screenshots (optional)
3. Maintainers can:
   - Pin popular presets
   - Add exceptional presets to built-in collection
   - Provide feedback and suggestions

### Curated Built-in Presets

Exceptional community presets can be promoted to built-in:
1. Community member submits preset via Discussion
2. Maintainer reviews and tests
3. If approved, added to `presets/builtin/` in next release
4. Original author credited in preset metadata

## Consequences

### Positive

- File export is simple and works offline
- No infrastructure to maintain
- GitHub Discussions provides community features (voting, comments)
- Low barrier to contribution
- Curated built-in presets ensure quality
- Works for non-programmers (no PRs required)

### Negative

- No centralized preset browser in-app
- Users must manually find/download presets
- Discoverability depends on GitHub Discussions activity

### Neutral

- Presets include author attribution
- Validation on import prevents malformed presets
- No automatic sync or updates

## Future Consideration

If demand exists, could add:
- In-app preset browser fetching from GitHub repo
- Search by mouse model or workflow
- One-click install of community presets

## References

- GitHub Discussions: https://docs.github.com/en/discussions
- [ADR-002](ADR-002-preset-file-format.md): Preset file format
- [ADR-005](ADR-005-persistence.md): Where imported presets are stored
