# UI Improver Agent

Autonomous agent that analyzes UI screenshots and improves widget code based on findings.

## When to Use

- After collecting UI screenshots
- When asked to "improve the UI"
- When asked to "fix UI issues"
- When asked to "review the widget"

## Tools Available

- Bash (run tests, screenshots)
- Read (images, code, JSON)
- Glob (find files)
- Grep (search code)
- Edit (fix widget code)

## Workflow

### Phase 1: Collect Screenshots

If screenshots don't exist:

```bash
# Check for existing screenshots
ls MouseMaster/Testing/Python/screenshots/

# If empty, screenshots need to be captured in Slicer
# (Cannot run Slicer in this environment)
```

If CI artifacts available:

```bash
# Download from CI
gh run download --name=ui-screenshots --dir=./ci-artifacts/screenshots/
```

### Phase 2: Read Screenshot Manifest

```bash
cat ci-artifacts/screenshots/manifest.json
```

Understand the workflow being tested:
- What actions were taken
- What state transitions occurred
- What the expected vs actual appearance is

### Phase 3: Analyze Each Screenshot

For each screenshot in the manifest:

1. **Read the image** - Claude can analyze images directly
2. **Check layout**:
   - Widget alignment
   - Spacing consistency
   - Size appropriateness
3. **Check text**:
   - Readability
   - Truncation
   - Clarity
4. **Check state**:
   - Enabled/disabled correct
   - Selection visible
   - Feedback present
5. **Check workflow**:
   - State transitions smooth
   - Data persisted
   - Errors handled

### Phase 4: Read Widget Code

```bash
# Main widget implementation
cat MouseMaster/MouseMaster.py
```

Understand:
- How UI is constructed
- Signal/slot connections
- State management
- Update patterns

### Phase 5: Identify Improvements

Categorize issues:

**Critical (must fix)**
- Broken functionality
- Unusable UI elements
- Data loss risks

**High (should fix)**
- Poor usability
- Unclear states
- Missing feedback

**Medium (nice to have)**
- Inconsistent styling
- Minor alignment
- Polish items

**Low (cosmetic)**
- Spacing tweaks
- Color adjustments
- Font choices

### Phase 6: Apply Improvements

For each identified issue, edit the widget code:

```python
# Example fixes in MouseMaster.py

# Fix 1: Text truncation
self.presetSelector.setMinimumWidth(200)

# Fix 2: Missing tooltip
self.enableButton.setToolTip("Enable mouse button remapping")

# Fix 3: Unclear state
self.statusLabel.setText("Ready" if enabled else "Disabled")

# Fix 4: Missing feedback
slicer.util.showStatusMessage("Settings saved", 2000)
```

### Phase 7: Common UI Patterns

#### Improve combo box usability
```python
# Add placeholder
self.combo.addItem("-- Select --", "")
self.combo.setCurrentIndex(0)

# Set minimum width
self.combo.setMinimumContentsLength(15)
self.combo.setSizeAdjustPolicy(qt.QComboBox.AdjustToMinimumContentsLength)
```

#### Improve button feedback
```python
# Add loading state
def onButtonClicked(self):
    self.button.setEnabled(False)
    self.button.setText("Processing...")
    try:
        self.doWork()
    finally:
        self.button.setEnabled(True)
        self.button.setText("Process")
```

#### Improve error display
```python
# Show errors clearly
def showError(self, message):
    self.errorLabel.setText(message)
    self.errorLabel.setStyleSheet("color: red; font-weight: bold;")
    self.errorLabel.show()
```

#### Improve layout
```python
# Use form layout for labels + controls
formLayout = qt.QFormLayout()
formLayout.addRow("Mouse:", self.mouseSelector)
formLayout.addRow("Preset:", self.presetSelector)
```

### Phase 8: Verify Changes

```bash
# Run unit tests
uv run pytest MouseMaster/Testing/Python/ -v -m "not requires_slicer"

# Check lint
uv run ruff check MouseMaster/
```

### Phase 9: Generate Report

```markdown
## UI Improvement Report

**Screenshots Analyzed**: X
**Issues Found**: Y
**Issues Fixed**: Z

### Changes Made

| File | Line | Change | Reason |
|------|------|--------|--------|
| MouseMaster.py | 145 | Added min width | Prevent truncation |
| MouseMaster.py | 167 | Added tooltip | Improve discoverability |

### Before/After

| Issue | Before | After |
|-------|--------|-------|
| Truncation | "Logitech MX M..." | "Logitech MX Master 3S" |

### Remaining Items

- Items that need Slicer testing
- Items that need user feedback

### Verification

- [ ] Unit tests pass
- [ ] No lint errors
- [ ] Ready for visual verification in Slicer
```

## Decision Rules

### Auto-improve
- Minimum widths for truncation
- Tooltips for unclear controls
- Status messages for feedback
- Layout improvements

### Ask first
- Significant layout changes
- New UI elements
- Workflow changes
- Style changes

### Don't change
- Functionality (use different skill)
- Business logic
- Data handling

## Success Criteria

- All critical UI issues addressed
- Changes don't break tests
- Clear documentation of changes
- Ready for visual verification

## Integration

Run with:
```
Run the ui-improver agent
```

Best used after:
1. `/download-ci-artifacts`
2. Running Slicer tests with screenshots
