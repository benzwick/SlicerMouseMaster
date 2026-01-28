# Claude Code Hooks

This directory contains recommended hook configurations for SlicerMouseMaster development.

## Recommended Hooks Configuration

Add these hooks to your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "uv run ruff format \"$FILE_PATH\" 2>/dev/null || true"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"[hook] Running: $COMMAND\""
          }
        ]
      }
    ]
  }
}
```

## Hook Descriptions

### PostToolUse: Edit -> Auto-format

After editing Python files, automatically format with ruff:
- Ensures consistent code style
- Runs silently (errors suppressed)
- Only affects Python files

### PreToolUse: Bash -> Command Logging

Before running bash commands, log them:
- Provides audit trail
- Helps with debugging
- Non-blocking (doesn't prevent execution)

## Additional Recommended Hooks

### Block Dangerous Commands

```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "block",
          "pattern": "rm -rf /",
          "message": "Dangerous command blocked"
        }
      ]
    }
  ]
}
```

### Validate Commit Messages

```json
{
  "PreToolUse": [
    {
      "matcher": "Bash(git commit*)",
      "hooks": [
        {
          "type": "command",
          "command": "echo 'Reminder: Use conventional commit format (feat:, fix:, etc.)'"
        }
      ]
    }
  ]
}
```

## Notes

- Hooks are configured per-user in `~/.claude/settings.json`
- Project-specific hooks can be suggested but not enforced
- See Claude Code documentation for full hook capabilities
