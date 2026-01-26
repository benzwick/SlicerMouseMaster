# Platform Test Matrix

Track cross-platform verification status for SlicerMouseMaster.

## Current Status

Last updated: 2026-01-26

### Operating Systems

| Platform | Version | Slicer | Status | Tester | Date | Notes |
|----------|---------|--------|--------|--------|------|-------|
| Linux | Debian 13 | 5.6+ | ✓ Verified | @benzwick | 2026-01-26 | Primary dev platform |
| Windows | 10/11 | 5.6+ | ⏳ Pending | - | - | |
| macOS | 13+ | 5.6+ | ⏳ Pending | - | - | |

### Mice Tested

| Mouse | Platform | Status | Tester | Date | Notes |
|-------|----------|--------|--------|------|-------|
| Logitech MX Master 3S | Linux | ⏳ Pending | - | - | |
| Logitech MX Master 4 | Linux | ⏳ Pending | - | - | |
| Generic 3-button | Linux | ⏳ Pending | - | - | |
| Generic 5-button | Linux | ⏳ Pending | - | - | |

### Feature Matrix

| Feature | Linux | Windows | macOS |
|---------|-------|---------|-------|
| Event interception | ✓ | ⏳ | ⏳ |
| Button detection | ✓ | ⏳ | ⏳ |
| Preset loading | ✓ | ⏳ | ⏳ |
| Context switching | ✓ | ⏳ | ⏳ |
| Settings persistence | ✓ | ⏳ | ⏳ |

---

## Verification Checklist

When testing on a new platform, verify:

### Core Functionality
- [ ] Module loads without errors
- [ ] Event handler installs successfully
- [ ] Button presses are detected (check Slicer console)
- [ ] Actions execute correctly (undo, redo, etc.)

### Button Detection
- [ ] Left/Right/Middle detected with correct codes
- [ ] Back/Forward detected (if mouse has them)
- [ ] Extra buttons detected (thumb, etc.)
- [ ] Button codes match expected Qt values

### Presets
- [ ] Built-in presets load
- [ ] Custom presets can be saved
- [ ] Presets persist after Slicer restart
- [ ] Export/import works

### Context Sensitivity
- [ ] Module detection works
- [ ] SegmentEditor bindings activate
- [ ] Default bindings used in other modules

### Platform-Specific
- [ ] No permission errors (Linux: input group)
- [ ] No system interception (macOS: accessibility)
- [ ] Vendor software compatibility (Logitech Options, etc.)

---

## Known Platform Differences

### Linux
- Qt button codes: Standard
- May need user in `input` group for some mice
- evdev fallback available for problematic mice

### Windows
- Qt button codes: May differ for extra buttons
- No special permissions needed
- Vendor software may intercept buttons

### macOS
- Qt button codes: May differ
- System may intercept gestures
- Accessibility permissions may be needed
- Ctrl/Cmd swap affects modifier detection

---

## How to Report Verification

When you verify a platform, update this file:

1. Update status in tables above (⏳ → ✓ or ✗)
2. Add tester name and date
3. Note any issues in the Notes column
4. If issues found, create GitHub issue with:
   - Platform details (OS version, Slicer version)
   - Mouse model
   - Steps to reproduce
   - Error messages or unexpected behavior

---

## Automated Tests

Unit tests run on all platforms:

```bash
uv run pytest MouseMaster/Testing/Python/ -v
```

These test the logic but not Slicer integration. Full verification requires manual testing in Slicer.

---

## CI Status

| Platform | CI | Status |
|----------|------|--------|
| Linux | GitHub Actions | Not configured |
| Windows | GitHub Actions | Not configured |
| macOS | GitHub Actions | Not configured |

Future: Add GitHub Actions workflow for cross-platform testing.
