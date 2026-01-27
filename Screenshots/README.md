# Screenshots

Screenshots for documentation and Extension Index submission.

## Required Screenshots

| Filename | Purpose | Status |
|----------|---------|--------|
| `main-ui.png` | Primary screenshot for Extension Index | ✅ Complete |
| `button-mapping.png` | Button mapping table detail | ✅ Complete |
| `preset-selector.png` | Preset management interface | ✅ Complete |

## Generating Screenshots

### Option 1: Run Script in Slicer

1. Open 3D Slicer
2. Load the MouseMaster module
3. Open Python console (View → Python Console)
4. Run:

```python
exec(open('/home/ben/projects/slicer-extensions/SlicerMouseMaster/SlicerMouseMaster/scripts/capture_screenshots.py').read())
capture_all_screenshots()
```

### Option 2: Manual Capture

1. Open MouseMaster module in Slicer
2. Arrange UI as desired
3. Use OS screenshot tool
4. Save to this directory with appropriate name

## Requirements for Extension Index

Per Slicer Extension Index requirements:

- **At least one screenshot required** for submission
- Must be accessible via raw GitHub URL
- Recommended: Show the module's main functionality
- Format: PNG preferred

## URL Format

After pushing to GitHub, screenshots will be available at:

```
https://raw.githubusercontent.com/benzwick/SlicerMouseMaster/main/SlicerMouseMaster/Screenshots/main-ui.png
```

Update `CMakeLists.txt` with this URL:

```cmake
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/benzwick/SlicerMouseMaster/main/SlicerMouseMaster/Screenshots/main-ui.png")
```

## Screenshot Guidelines

1. **Resolution**: At least 800x600, ideally 1200x800
2. **Content**: Show module in active use with sample data
3. **Clean UI**: Remove any personal data or irrelevant windows
4. **Consistent**: Use similar layout across screenshots
