# Frequently Asked Questions

## General

### What mice are supported?

MouseMaster supports any mouse, but works best with mice that have extra programmable buttons. Built-in profiles are provided for:

- Generic 3-button mice (left, right, middle)
- Generic 5-button mice (adds back/forward)
- Logitech MX Master 3S
- Logitech MX Master 4

For other mice, use the "Detect New Mouse..." feature to create a custom profile.

### Does MouseMaster work with trackpads?

MouseMaster is designed for mice with extra buttons. Standard trackpads typically don't have the additional buttons that MouseMaster maps. However, if your trackpad has extra gesture buttons that register as mouse buttons, you can try the button detection feature.

### Which Slicer versions are supported?

MouseMaster requires 3D Slicer 5.0 or later. It's tested with the latest stable release.

## Button Mapping

### Why don't my mappings work?

Check these common issues:

1. **MouseMaster not enabled**: Click "Enable Mouse Master" button
2. **No preset selected**: Select a preset from the dropdown
3. **Wrong mouse selected**: Ensure your mouse model matches
4. **Button not remappable**: Left and right click are typically not remappable
5. **Conflicting software**: Disable vendor software (Logitech Options+, etc.) that may intercept buttons

### Can I remap left and right click?

No. Left and right click are essential for Slicer's core functionality and cannot be remapped. MouseMaster focuses on extra buttons (middle click, back, forward, thumb buttons, etc.).

### How do I create context-sensitive bindings?

1. Open the "Button Mappings" section
2. Check "Enable context-sensitive bindings"
3. Select a context (e.g., "Segment Editor")
4. Configure button mappings for that context
5. Repeat for other contexts as needed

Bindings set for a specific context override the default bindings only when that module is active.

### Why does my back button still navigate in the browser?

Some mice have hardware-level back/forward button mappings that can't be overridden by software. Try:

1. Use vendor software (Logitech Options+, etc.) to disable the button's default action
2. Map the button to a neutral action in vendor software
3. Use a different button

## Presets

### Where are presets stored?

- **Built-in presets**: `<Slicer Install>/lib/Slicer-X.X/qt-scripted-modules/presets/builtin/`
- **User presets**: `<User Settings>/MouseMaster/presets/`

On Windows, user settings are typically in `%LOCALAPPDATA%/NA-MIC/Slicer X.X-YYYY-MM-DD/`.

### How do I share my preset?

1. Configure your mappings in MouseMaster
2. The preset is automatically saved
3. Find the preset JSON file in your user presets directory
4. Share the file via email, GitHub, or other means

See [Contributing Presets](contributing-presets.md) for detailed instructions.

### Can I use presets from other users?

Yes! To import a preset:

1. Place the `.json` file in your user presets directory
2. Restart Slicer or reload the MouseMaster module
3. The preset will appear in the preset dropdown

## Custom Mice

### How do I add support for my mouse?

1. Open MouseMaster
2. Click "Detect New Mouse..."
3. Follow the prompts to press each button
4. Name your mouse profile
5. Click "Save Profile"

The profile is saved to your user settings and persists across sessions.

### What do the button codes mean?

Button codes are Qt's internal representation of mouse buttons:

| Code | Standard Meaning |
|------|------------------|
| 1 | Left click |
| 2 | Right click |
| 4 | Middle click |
| 8 | Back / Button 4 |
| 16 | Forward / Button 5 |
| 32+ | Additional buttons |

These may vary by platform and mouse model.

## Troubleshooting

### MouseMaster causes Slicer to crash

1. Disable MouseMaster and restart Slicer
2. Check the Slicer error log for details
3. Report the issue with log contents

### Buttons stopped working after Slicer update

Slicer updates may change internal APIs. Try:

1. Reinstall the MouseMaster extension
2. Reset your presets by deleting the user preset directory
3. Report the issue if it persists

### How do I reset MouseMaster?

To reset all settings:

1. Close Slicer
2. Delete `<User Settings>/MouseMaster/`
3. Restart Slicer

### Where are the logs?

MouseMaster logs to the Slicer Python console. To view:

1. View → Python Console
2. Look for messages prefixed with `[MouseMaster]`

## Platform-Specific

### Windows: Buttons not detected

- Run Slicer as Administrator (temporarily, for testing)
- Check if another application is capturing the buttons
- Disable gaming software overlays

### macOS: Permission issues

- System Preferences → Security & Privacy → Privacy → Accessibility
- Ensure Slicer has accessibility permissions

### Linux: X11 vs Wayland

MouseMaster works best with X11. On Wayland, button detection may be limited due to security restrictions. Try running Slicer with XWayland.

## Advanced

### Can I execute Python code with a button?

Yes! Use the "Python command" action type:

```json
{
  "action": "python_command",
  "parameters": {
    "command": "slicer.util.selectModule('SegmentEditor')"
  }
}
```

### Can I simulate keyboard shortcuts?

Yes! Use the "Keyboard shortcut" action type:

```json
{
  "action": "keyboard_shortcut",
  "parameters": {
    "key": "Z",
    "modifiers": ["ctrl"]
  }
}
```

### How do I trigger menu actions?

MouseMaster discovers Slicer menu actions automatically. They appear in the action dropdown as "slicer_menu_ActionName". You can also specify them directly:

```json
{
  "action": "slicer_menu_EditUndo"
}
```

## Getting Help

### Where can I report bugs?

Open an issue on GitHub: [SlicerMouseMaster Issues](https://github.com/username/SlicerMouseMaster/issues)

Include:
- Slicer version
- OS and version
- Steps to reproduce
- Error messages from Python console

### Where can I request features?

Open a feature request issue on GitHub or start a discussion in the Slicer Discourse forum.
