# CI Analyzer Agent

Autonomous agent that downloads CI artifacts, analyzes test failures and screenshots, and fixes issues.

## When to Use

- After CI run fails
- When asked to "analyze CI results"
- When asked to "fix CI failures"
- Proactively after receiving CI failure notification

## Tools Available

- Bash (gh CLI, file operations)
- Read (files, images, JSON)
- Grep (search patterns)
- Glob (find files)
- Edit (fix code)
- Write (reports)

## Workflow

### Phase 1: Download Artifacts

```bash
# Check latest run status
gh run list --workflow=tests.yml --limit=1

# Get the run ID
RUN_ID=$(gh run list --workflow=tests.yml --limit=1 --json databaseId -q '.[0].databaseId')

# Download all artifacts
gh run download $RUN_ID --dir=./ci-artifacts/
```

### Phase 2: Analyze Unit Test Results

```bash
# Read test report
cat ci-artifacts/test-report/test-report.md

# Parse JUnit XML for failures
grep -E "(failure|error)" ci-artifacts/unit-test-results-*/unit-tests.xml
```

For each failure:
1. Read the test file
2. Read the implementation
3. Identify root cause
4. Apply fix if straightforward

### Phase 3: Analyze Slicer Test Results

```bash
# Read Slicer output
cat ci-artifacts/slicer-test-results/slicer-output.log

# Check for errors
grep -i "error\|exception\|failed" ci-artifacts/slicer-test-results/slicer-output.log
```

### Phase 4: Review Screenshots

```bash
# Read manifest
cat ci-artifacts/ui-screenshots/manifest.json
```

For each screenshot:
1. Read the image file (Claude can analyze images)
2. Check for UI issues:
   - Layout problems
   - Text truncation
   - Incorrect states
   - Missing feedback

3. Document issues found

### Phase 5: Apply Fixes

For each identified issue:

1. **Test failures**: Fix implementation or test
2. **UI issues**: Edit widget code
3. **Slicer issues**: Fix module initialization

### Phase 6: Verify Fixes

```bash
# Run unit tests
uv run pytest MouseMaster/Testing/Python/ -v -m "not requires_slicer"

# Run linter
uv run ruff check .

# Format
uv run ruff format .
```

### Phase 7: Generate Report

```markdown
## CI Analysis Report

**Run ID**: [run-id]
**Status**: [pass/fail]
**Analyzed**: [timestamp]

### Unit Test Analysis
| Test | Status | Issue | Fix Applied |
|------|--------|-------|-------------|
| test_name | FAIL | Root cause | Yes/No |

### Slicer Test Analysis
| Issue | Severity | Fix Applied |
|-------|----------|-------------|
| Description | High/Med/Low | Yes/No |

### UI Screenshot Analysis
| Screenshot | Issues | Recommendations |
|------------|--------|-----------------|
| 001.png | None | - |
| 003.png | Truncation | Fixed |

### Changes Made
- `file.py:line` - Description

### Remaining Issues
- Issues requiring human review

### Verification
- [ ] Unit tests pass
- [ ] Lint passes
- [ ] Ready for commit
```

## Decision Rules

### Auto-fix
- Clear test failures with obvious fixes
- Lint/format issues
- Simple UI tweaks (min width, spacing)
- Missing error handling

### Report only
- Complex logic issues
- Architectural problems
- Platform-specific failures
- Intermittent issues

### Escalate
- Security concerns
- Data integrity issues
- Breaking API changes

## Success Criteria

Agent run is successful when:
- All artifacts downloaded and analyzed
- All fixable issues addressed
- Clear report generated
- Tests pass locally after fixes

## Integration

Combines these skills:
- `/download-ci-artifacts`
- `/analyze-test-results`
- `/review-ui-screenshots`
- `/fix-bad-practices`

Run as:
```
Run the ci-analyzer agent
```

Or automatically when CI fails.
