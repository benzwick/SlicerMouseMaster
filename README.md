# SlicerMouseMaster

A 3D Slicer extension for advanced mouse customization, button remapping, and workflow optimization.

![SlicerMouseMaster Main Interface](SlicerMouseMaster/Screenshots/main-ui.png)

**[Full Documentation](https://benzwick.github.io/SlicerMouseMaster)** | [User Guide](https://benzwick.github.io/SlicerMouseMaster/user-guide/) | [Developer Guide](https://benzwick.github.io/SlicerMouseMaster/developer-guide/)

## Features

- **Button Remapping**: Assign custom actions to mouse buttons (back, forward, thumb, etc.)
- **Mouse Profiles**: Built-in support for popular mice with auto-detection
- **Workflow Presets**: Save and share button configurations for different tasks
- **Context-Sensitive Bindings**: Different mappings per Slicer module
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Supported Mice

| Mouse | Vendor ID | Buttons | Status |
|-------|-----------|---------|--------|
| Logitech MX Master 3S | 0x46D | 7 | Fully Supported |
| Logitech MX Master 4 | 0x46D | 7 | Fully Supported |
| Generic 3-Button | Any | 3 | Basic Support |
| Generic 5-Button | Any | 5 | Basic Support |

Don't see your mouse? Use the button detection wizard to create a custom profile.

## Installation

### From Extension Manager (Recommended)

1. Open 3D Slicer
2. Go to **View > Extension Manager**
3. Search for "MouseMaster"
4. Click **Install**
5. Restart Slicer

### From Source

```bash
git clone https://github.com/benzwick/SlicerMouseMaster.git
# Add to Slicer's module paths
```

## Quick Start

1. **Open the Module**: Navigate to **Modules > Utilities > MouseMaster**

2. **Select Your Mouse**: Choose your mouse model from the dropdown, or use "Auto-Detect"

3. **Choose or Create a Preset**:
   - Select a built-in preset for common workflows
   - Or create your own by clicking "New Preset"

4. **Customize Bindings**:
   - Click on a button in the mapping table
   - Choose an action from the dropdown
   - Changes apply immediately

5. **Save Your Preset**: Click "Save Preset" to keep your configuration

## Usage Guide

### Default Bindings (MX Master 3S/4)

| Button | Default Action | Segment Editor Override |
|--------|---------------|------------------------|
| Back | Undo | Previous Segment |
| Forward | Redo | Next Segment |
| Thumb | Toggle Crosshair | Toggle Paint/Erase |
| Middle Click | Reset 3D View | (No override) |

### Context-Sensitive Bindings

MouseMaster automatically detects which Slicer module is active and can apply different bindings:

- **Segment Editor**: Optimized for segmentation workflow
- **Markups**: Quick placement and editing
- **Volume Rendering**: View manipulation shortcuts
- **Default**: Fallback bindings for all other modules

### Creating a Custom Profile

If your mouse isn't listed:

1. Click **"Detect New Mouse"**
2. Press each button when prompted
3. Name and save your profile
4. Your mouse will be available in the dropdown

### Sharing Presets

**Export a Preset:**
1. Select the preset you want to share
2. Click **"Export Preset"**
3. Choose a location to save the .json file

**Import a Preset:**
1. Click **"Import Preset"**
2. Select a .json preset file
3. The preset will be added to your list

**Community Presets:**
Browse community-submitted presets at our [GitHub Discussions](https://github.com/benzwick/SlicerMouseMaster/discussions/categories/presets).

## Available Actions

### Navigation
- Reset 3D View
- Zoom In / Zoom Out
- Pan View
- Rotate View

### Editing
- Undo / Redo
- Delete Selected
- Toggle Crosshair

### Segment Editor
- Next/Previous Segment
- Toggle Effect (Paint/Erase)
- Apply Effect
- Show/Hide Segment

### Custom Actions
- Run Slicer Python command
- Trigger menu action by name
- Keyboard shortcut simulation

## Troubleshooting

### Button presses not detected

1. Ensure MouseMaster module is loaded (check module selector)
2. Verify your mouse is recognized by the operating system
3. Try the "Detect Buttons" wizard to confirm button codes
4. On Linux, you may need to add yourself to the `input` group

### Presets not saving

1. Check you have write permissions to the Slicer settings directory
2. Try exporting to a specific location instead
3. Check the Slicer Python console for error messages

### Bindings not working in specific module

1. Ensure the module is listed in context-sensitive settings
2. Check if another extension is consuming the button events
3. Try setting higher priority in advanced settings

### Cross-platform differences

Button codes may differ between operating systems. If a preset created on Windows doesn't work on Linux:
1. Re-detect buttons using the wizard
2. Save as a new platform-specific preset

## Requirements

- 3D Slicer 5.4 or later
- Python 3.9+
- No additional dependencies (uses Qt/VTK from Slicer)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Reporting Bugs

1. Check existing issues on GitHub
2. Include: Slicer version, OS, mouse model, steps to reproduce
3. Attach relevant preset files if applicable

### Submitting Presets

Share your workflow presets with the community:
1. Export your preset to JSON
2. Create a Discussion post in the "Presets" category
3. Include: mouse model, workflow description, any special setup

## Documentation

For comprehensive documentation, visit the [documentation site](https://benzwick.github.io/SlicerMouseMaster):

- [Installation Guide](https://benzwick.github.io/SlicerMouseMaster/user-guide/installation.html)
- [Quick Start](https://benzwick.github.io/SlicerMouseMaster/user-guide/quick-start.html)
- [Button Mapping](https://benzwick.github.io/SlicerMouseMaster/user-guide/button-mapping.html)
- [Developer Guide](https://benzwick.github.io/SlicerMouseMaster/developer-guide/)

## License

This project is licensed under the Apache License 2.0. See [LICENSE.txt](LICENSE.txt) for details.

## Acknowledgments

- 3D Slicer community for the excellent platform
- Contributors who submitted mouse profiles and presets
