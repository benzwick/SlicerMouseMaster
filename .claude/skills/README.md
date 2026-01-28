# SlicerMouseMaster Claude Skills

Structured instructions that guide Claude through specific SlicerMouseMaster development tasks.

Invoke skills by typing `/skill-name` in Claude Code.

## Code Quality Philosophy

This project follows **fail-fast, test-driven development** for human-LLM collaboration:

1. **Fail Fast** - Errors surface immediately, never hidden
2. **Explicit Over Silent** - No `except: pass`, no silent `continue`
3. **Log Everything** - All exceptions logged for debugging
4. **Test First** - Tests catch bugs, not error suppression
5. **Clear Signals** - Detailed logs enable autonomous debugging

### Why This Matters

When Claude works on this codebase:
- **Clear test output** - Claude can run tests and understand results
- **Explicit errors** - Claude can identify and fix real issues
- **Detailed logs** - Claude can trace problems through execution
- **No hidden state** - Code behavior matches what Claude reads
- **Autonomous maintenance** - Claude can audit, fix, and verify

### Anti-Patterns (Never Use)

```python
# NEVER: Silent exception swallowing
except: pass
except Exception: pass

# NEVER: Silent continuation
if error: continue

# NEVER: Unlogged exceptions
except SomeError:
    return default  # No logging!
```

## All Skills

| Skill | Purpose |
|-------|---------|
| `/add-mouse-profile` | Create support for a new mouse model |
| `/detect-buttons` | Discover Qt button codes for unknown mice |
| `/test-bindings` | Debug and verify button bindings |
| `/export-preset` | Export preset configurations |
| `/run-tests` | Run tests, lint, typecheck, and audit |
| `/audit-code-quality` | Scan for fail-fast violations |
| `/fix-bad-practices` | Fix exception swallowing and error hiding |
| `/autonomous-code-review` | Full autonomous review and fix workflow |
| `/generate-screenshots` | Capture UI screenshots for documentation |
| `/extension-submission-checklist` | Review official Slicer requirements |
| `/prepare-extension-metadata` | Generate CMakeLists.txt and JSON metadata |
| `/validate-extension-submission` | Automated validation before submission |
| `/submit-to-extension-index` | Complete submission workflow |

## Recommended Workflows

### Adding Mouse Support

```
1. /detect-buttons           # Discover button codes
2. /add-mouse-profile        # Create profile JSON
3. /test-bindings            # Verify bindings work
```

### Extension Index Submission

```
1. /generate-screenshots             # Capture UI screenshots
2. /prepare-extension-metadata       # Update metadata files
3. /validate-extension-submission    # Run automated checks
4. /submit-to-extension-index        # Complete submission
```

### Code Quality

Quick check:
```
/run-tests                   # Tests, lint, typecheck, audit
```

Detailed:
```
1. /audit-code-quality       # Scan for bad practices
2. /fix-bad-practices        # Fix identified issues
3. /run-tests                # Verify fixes
```

Autonomous:
```
/autonomous-code-review      # Full audit, fix, verify cycle
```

## Agents

See `.claude/agents/` for autonomous workflows that combine multiple skills.

| Agent | Purpose |
|-------|---------|
| `test-runner` | Run tests + lint + audit + report |

## Support

- **Issues**: https://github.com/benzwick/SlicerMouseMaster/issues
- **Slicer Forum**: https://discourse.slicer.org
- **Extension Docs**: https://slicer.readthedocs.io/en/latest/developer_guide/extensions.html
