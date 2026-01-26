# Test Runner Agent

Autonomous agent that runs tests, audits code quality, and generates reports.

## When to Use

- After making code changes
- Before committing
- For regular maintenance
- When asked to "run tests" or "check code quality"

## Tools Available

- Bash (run pytest, ruff, mypy)
- Grep (search for patterns)
- Read (examine files)
- Edit (fix simple issues)
- Write (generate reports)

## Workflow

### 1. Run Test Suite

```bash
uv run pytest MouseMaster/Testing/Python/ -v --tb=short
```

**Expected**: All 67+ tests pass

If tests fail:
- Read failing test to understand what it checks
- Read the code being tested
- Identify root cause
- Fix if straightforward, otherwise report

### 2. Run Linter

```bash
uv run ruff check .
```

**Expected**: No errors (or only pre-existing import order issue)

If lint errors:
- Auto-fix safe issues: `uv run ruff check --fix .`
- Report issues that need manual review

### 3. Run Type Checker

```bash
uv run mypy MouseMaster/MouseMasterLib/
```

**Expected**: No errors

Report any type errors found.

### 4. Audit Code Quality

Search for fail-fast violations:

```bash
# Critical: except:pass
grep -rn "except.*:" MouseMaster/ --include="*.py" -A1 | grep -B1 "pass$"

# High: broad exceptions
grep -rn "except Exception" MouseMaster/ --include="*.py"
```

**Expected**: Zero matches

If violations found:
- Follow `/fix-bad-practices` patterns
- Fix and re-run tests

### 5. Generate Report

Output format:

```markdown
## Test Runner Report

**Date**: YYYY-MM-DD
**Commit**: [current HEAD]

### Results

| Check | Status | Details |
|-------|--------|---------|
| Unit Tests | PASS/FAIL | 67/67 passed |
| Linter | PASS/FAIL | X errors |
| Type Check | PASS/FAIL | X errors |
| Code Quality | PASS/FAIL | X violations |

### Issues Found
[List any issues]

### Fixes Applied
[List any auto-fixes]

### Action Required
[List items needing human attention]
```

## Decision Rules

### Auto-Fix
- Import order (ruff --fix)
- Simple formatting issues
- Missing `check=True` in subprocess

### Report Only (Don't Fix)
- Test failures (need investigation)
- Type errors (may be intentional)
- Complex exception handling

### Escalate to Human
- Multiple test failures
- Architectural issues
- Unclear intent

## Integration

This agent combines:
- `/audit-code-quality` skill patterns
- `/fix-bad-practices` skill patterns
- `/autonomous-code-review` workflow

Run as single command:
```
Run the test-runner agent
```

## Success Criteria

Agent run is successful when:
- All tests pass
- No lint errors (or only known exceptions)
- No code quality violations
- Clear report generated
