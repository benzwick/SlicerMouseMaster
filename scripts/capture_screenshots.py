#!/usr/bin/env python
"""
Screenshot capture script for SlicerMouseMaster.

Run this script in Slicer's Python console to capture screenshots
for Extension Index submission and documentation.

Usage in Slicer Python console:
    exec(open('/path/to/scripts/capture_screenshots.py').read())

Or import and call functions individually:
    from scripts.capture_screenshots import capture_main_ui
    capture_main_ui('/path/to/Screenshots')
"""

import os
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


def get_screenshot_dir() -> Path:
    """Get the Screenshots directory path."""
    # Try to find it relative to this script
    script_dir = Path(__file__).parent if '__file__' in dir() else Path.cwd()

    # Check common locations
    candidates = [
        script_dir.parent / "Screenshots",
        script_dir / "Screenshots",
        Path.cwd() / "Screenshots",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    # Default to first candidate
    screenshots_dir = candidates[0]
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    return screenshots_dir


def capture_widget(widget, filepath: Path, size: tuple[int, int] | None = None) -> bool:
    """Capture a Qt widget to an image file.

    Args:
        widget: Qt widget to capture
        filepath: Output file path
        size: Optional (width, height) to resize

    Returns:
        True if successful
    """
    import qt

    try:
        # Grab the widget
        pixmap = qt.QPixmap.grabWidget(widget)

        # Resize if requested
        if size:
            pixmap = pixmap.scaled(
                size[0], size[1],
                qt.Qt.KeepAspectRatio,
                qt.Qt.SmoothTransformation
            )

        # Save
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        success = pixmap.save(str(filepath))
        if success:
            logger.info(f"Saved screenshot: {filepath}")
        else:
            logger.error(f"Failed to save screenshot: {filepath}")
        return success

    except Exception as e:
        logger.exception(f"Error capturing widget: {e}")
        return False


def capture_main_window(filepath: Path, size: tuple[int, int] | None = None) -> bool:
    """Capture the entire Slicer main window.

    Args:
        filepath: Output file path
        size: Optional (width, height) to resize

    Returns:
        True if successful
    """
    import slicer
    return capture_widget(slicer.util.mainWindow(), filepath, size)


def capture_module_panel(filepath: Path) -> bool:
    """Capture just the module panel (right side).

    Args:
        filepath: Output file path

    Returns:
        True if successful
    """
    import slicer

    # Find the module panel widget
    main_window = slicer.util.mainWindow()
    module_panel = main_window.findChild("QWidget", "ModulePanel")

    if module_panel:
        return capture_widget(module_panel, filepath)
    else:
        logger.error("Could not find ModulePanel widget")
        return False


def capture_3d_view(filepath: Path, size: tuple[int, int] | None = None) -> bool:
    """Capture the 3D view.

    Args:
        filepath: Output file path
        size: Optional (width, height) to resize

    Returns:
        True if successful
    """
    import slicer

    layout_manager = slicer.app.layoutManager()
    if layout_manager.threeDViewCount > 0:
        three_d_widget = layout_manager.threeDWidget(0)
        view = three_d_widget.threeDView()
        return capture_widget(view, filepath, size)
    else:
        logger.error("No 3D view available")
        return False


def ensure_mousemaster_visible() -> bool:
    """Ensure MouseMaster module is visible and active.

    Returns:
        True if successful
    """
    import slicer

    try:
        # Switch to MouseMaster module
        slicer.util.selectModule("MouseMaster")

        # Give UI time to update
        import qt
        qt.QApplication.processEvents()

        return True
    except Exception as e:
        logger.error(f"Could not switch to MouseMaster module: {e}")
        return False


def capture_main_ui(output_dir: Path | str | None = None) -> Path | None:
    """Capture the main MouseMaster UI screenshot.

    This is the primary screenshot for Extension Index submission.
    Shows the module panel with MouseMaster controls.

    Args:
        output_dir: Directory to save screenshot (default: Screenshots/)

    Returns:
        Path to saved screenshot, or None if failed
    """
    import slicer
    import qt

    output_dir = Path(output_dir) if output_dir else get_screenshot_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Ensure module is visible
    if not ensure_mousemaster_visible():
        return None

    # Wait for UI to settle
    qt.QApplication.processEvents()

    # Capture main window with module visible
    filepath = output_dir / "main-ui.png"

    if capture_main_window(filepath, size=(1200, 800)):
        print(f"✓ Captured main UI: {filepath}")
        return filepath
    return None


def capture_button_mapping(output_dir: Path | str | None = None) -> Path | None:
    """Capture the button mapping table.

    Args:
        output_dir: Directory to save screenshot

    Returns:
        Path to saved screenshot, or None if failed
    """
    import slicer
    import qt

    output_dir = Path(output_dir) if output_dir else get_screenshot_dir()

    if not ensure_mousemaster_visible():
        return None

    qt.QApplication.processEvents()

    # Try to find and capture just the mapping table
    # Fall back to full module panel
    filepath = output_dir / "button-mapping.png"

    if capture_module_panel(filepath):
        print(f"✓ Captured button mapping: {filepath}")
        return filepath
    return None


def capture_preset_selector(output_dir: Path | str | None = None) -> Path | None:
    """Capture the preset selector dropdown.

    Args:
        output_dir: Directory to save screenshot

    Returns:
        Path to saved screenshot, or None if failed
    """
    import slicer
    import qt

    output_dir = Path(output_dir) if output_dir else get_screenshot_dir()

    if not ensure_mousemaster_visible():
        return None

    qt.QApplication.processEvents()

    filepath = output_dir / "preset-selector.png"

    if capture_module_panel(filepath):
        print(f"✓ Captured preset selector: {filepath}")
        return filepath
    return None


def capture_all_screenshots(output_dir: Path | str | None = None) -> dict[str, Path | None]:
    """Capture all screenshots needed for documentation.

    Args:
        output_dir: Directory to save screenshots

    Returns:
        Dict mapping screenshot name to file path (or None if failed)
    """
    output_dir = Path(output_dir) if output_dir else get_screenshot_dir()

    print(f"Capturing screenshots to: {output_dir}")
    print("=" * 50)

    results = {
        "main-ui": capture_main_ui(output_dir),
        "button-mapping": capture_button_mapping(output_dir),
        "preset-selector": capture_preset_selector(output_dir),
    }

    print("=" * 50)

    # Summary
    success = sum(1 for v in results.values() if v is not None)
    total = len(results)
    print(f"Captured {success}/{total} screenshots")

    if success < total:
        failed = [k for k, v in results.items() if v is None]
        print(f"Failed: {', '.join(failed)}")

    return results


def generate_manifest(output_dir: Path | str | None = None) -> Path:
    """Generate a manifest.json describing all screenshots.

    Args:
        output_dir: Screenshots directory

    Returns:
        Path to manifest file
    """
    import json

    output_dir = Path(output_dir) if output_dir else get_screenshot_dir()

    # Find all PNG files
    screenshots = list(output_dir.glob("*.png"))

    manifest = {
        "generated": datetime.now().isoformat(),
        "screenshots": []
    }

    descriptions = {
        "main-ui.png": "Main MouseMaster interface showing button mapping configuration",
        "button-mapping.png": "Button mapping table with action assignments",
        "preset-selector.png": "Preset selection and management interface",
    }

    for screenshot in sorted(screenshots):
        entry = {
            "filename": screenshot.name,
            "description": descriptions.get(screenshot.name, "Screenshot"),
            "size_bytes": screenshot.stat().st_size,
        }
        manifest["screenshots"].append(entry)

    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated manifest: {manifest_path}")
    return manifest_path


def main() -> int:
    """Main entry point for command-line execution.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    import sys

    print("SlicerMouseMaster Screenshot Capture")
    print("=" * 50)

    # Parse arguments
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    should_exit = "--exit" in args
    interactive = "--interactive" in args or (not should_exit and not args)

    if interactive:
        # Interactive mode - just print help
        print()
        print("Available functions:")
        print("  capture_main_ui()        - Main UI screenshot (for submission)")
        print("  capture_button_mapping() - Button mapping table")
        print("  capture_preset_selector()- Preset selector")
        print("  capture_all_screenshots()- All screenshots")
        print("  generate_manifest()      - Create manifest.json")
        print()
        print("Example:")
        print("  capture_all_screenshots()")
        print()
        return 0

    # Automatic mode - capture all screenshots
    print()
    print("Capturing screenshots automatically...")
    print()

    # Wait for Slicer UI to be ready
    import qt
    qt.QApplication.processEvents()

    # Capture all screenshots
    results = capture_all_screenshots()

    # Generate manifest
    generate_manifest()

    # Count successes
    success = sum(1 for v in results.values() if v is not None)
    total = len(results)

    print()
    print("=" * 50)
    print(f"Result: {success}/{total} screenshots captured")

    exit_code = 0 if success > 0 else 1

    if should_exit:
        print(f"Exiting Slicer with code {exit_code}")
        import slicer
        slicer.app.exit(exit_code)

    return exit_code


# Main execution when run in Slicer
if __name__ == "__main__" or "slicer" in dir():
    # Check if we're being run as a script (has sys.argv) or exec'd
    import sys
    if hasattr(sys, 'argv') and len(sys.argv) > 0 and 'capture_screenshots' in sys.argv[0]:
        # Running as: Slicer --python-script capture_screenshots.py [--exit]
        main()
    else:
        # Being exec'd in console - show help
        print("SlicerMouseMaster Screenshot Capture")
        print("=" * 50)
        print()
        print("Available functions:")
        print("  capture_main_ui()        - Main UI screenshot (for submission)")
        print("  capture_button_mapping() - Button mapping table")
        print("  capture_preset_selector()- Preset selector")
        print("  capture_all_screenshots()- All screenshots")
        print("  generate_manifest()      - Create manifest.json")
        print()
        print("Or run automatically:")
        print("  main()  # Capture all and generate manifest")
        print()
