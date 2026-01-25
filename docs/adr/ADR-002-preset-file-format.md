# ADR-002: Preset File Format

## Status

Accepted

## Context

Users need to save and share their button mapping configurations. The preset format must:

- Be human-readable for manual editing
- Support versioning for future compatibility
- Include mouse-specific mappings
- Support context-sensitive bindings
- Be easy to validate
- Be shareable between users

Options considered:
1. **JSON**: Universal, human-readable, schema validation available
2. **YAML**: More readable than JSON, but adds dependency
3. **TOML**: Good for config, less common for data
4. **INI/Settings**: Limited nested structure support
5. **Custom binary**: Not human-readable

## Decision

Use **JSON** for preset files with the following structure:

```json
{
  "$schema": "https://slicermousemaster.github.io/schemas/preset-v1.json",
  "id": "unique_preset_id",
  "name": "Human Readable Name",
  "version": "1.0",
  "mouseId": "logitech_mx_master_3s",
  "author": "optional author name",
  "description": "optional description",
  "mappings": {
    "button_id": {
      "action": "action_type",
      "actionId": "specific_action",
      "parameters": {}
    }
  },
  "contextMappings": {
    "ModuleName": {
      "button_id": {
        "action": "action_type",
        "actionId": "specific_action"
      }
    }
  }
}
```

Key format decisions:
- `$schema` field for JSON Schema validation
- `version` field for migration support
- `mouseId` links to mouse definition
- `mappings` for default bindings
- `contextMappings` for module-specific overrides

## Consequences

### Positive

- JSON is universally supported and familiar
- No additional dependencies required
- JSON Schema provides validation
- Version field enables future migrations
- Easy to share via copy/paste or file transfer
- Human-editable with any text editor
- Git-friendly for version control

### Negative

- JSON doesn't support comments (users may want to document)
- More verbose than YAML for deeply nested structures
- No trailing commas allowed (common editing error)

### Neutral

- Schema validation is optional but recommended
- Need to handle malformed JSON gracefully

## References

- JSON Schema: https://json-schema.org/
- [ADR-007](ADR-007-preset-sharing.md): Preset sharing mechanism
- [ADR-005](ADR-005-persistence.md): Where presets are stored
