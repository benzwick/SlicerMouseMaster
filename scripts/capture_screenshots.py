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

import logging
from datetime import datetime
from pathlib import Path

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
        # Grab the widget using modern API
        pixmap = widget.grab()

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
    import qt
    import slicer

    try:
        # Switch to MouseMaster module
        slicer.util.selectModule("MouseMaster")

        # Give UI time to update
        qt.QApplication.processEvents()

        return True
    except Exception as e:
        logger.error(f"Could not switch to MouseMaster module: {e}")
        return False


def setup_clean_ui(layout: str = "3d_only") -> None:
    """Set up a clean UI state for screenshots.

    - Hides Python console, Data Probe, and other panels
    - Sets specified layout
    - Collapses developer-focused sections

    Args:
        layout: Layout to use - "3d_only", "conventional", or "dual3d"
    """
    import qt
    import slicer

    main_window = slicer.util.mainWindow()

    # Hide all dock widgets that aren't needed
    dock_widgets_to_hide = [
        "PythonConsoleDockWidget",
        "PythonInteractorDockWidget",
        "DataProbeDockWidget",
        "ErrorLogDockWidget",
    ]

    for dock_name in dock_widgets_to_hide:
        try:
            dock = main_window.findChild(qt.QDockWidget, dock_name)
            if dock:
                dock.hide()
                logger.info(f"Hidden: {dock_name}")
        except Exception as e:
            logger.warning(f"Could not hide {dock_name}: {e}")

    # Also try to find Data Probe by other means (it's a collapsible widget)
    try:
        # Find all dock widgets and hide any that contain "DataProbe" or "Python"
        all_docks = main_window.findChildren(qt.QDockWidget)
        for dock in all_docks:
            dock_title = dock.windowTitle if hasattr(dock, 'windowTitle') else ""
            if callable(dock_title):
                dock_title = dock_title()
            if dock_title and ("Data Probe" in dock_title or "Python" in dock_title):
                dock.hide()
                logger.info(f"Hidden dock by title: {dock_title}")
    except Exception as e:
        logger.warning(f"Could not search dock widgets: {e}")

    # Set layout based on preference
    layout_map = {
        "3d_only": slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView,
        "conventional": slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView,
        "dual3d": slicer.vtkMRMLLayoutNode.SlicerLayoutDual3DView,
    }

    try:
        layout_id = layout_map.get(layout, slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView)
        slicer.app.layoutManager().setLayout(layout_id)
        logger.info(f"Set layout to: {layout}")
    except Exception as e:
        logger.warning(f"Could not set layout: {e}")

    qt.QApplication.processEvents()


def configure_module_sections(
    expand: list[str] | None = None,
    collapse: list[str] | None = None
) -> None:
    """Configure collapsible sections in MouseMaster module.

    Args:
        expand: List of section name patterns to expand
        collapse: List of section name patterns to collapse
    """
    import ctk
    import qt
    import slicer

    if expand is None:
        expand = ["Button Mappings", "Mouse Selection", "Preset Management"]
    if collapse is None:
        # Use partial matches to handle variations in section names
        collapse = ["Reload", "Help", "Data Probe", "Test"]

    main_window = slicer.util.mainWindow()

    # Search in multiple places for collapsible buttons
    search_areas = []

    # Module panel (main area for module widgets)
    module_panel = main_window.findChild(qt.QWidget, "ModulePanel")
    if module_panel:
        search_areas.append(("ModulePanel", module_panel))

    # Also search the entire main window for Data Probe and other sections
    search_areas.append(("MainWindow", main_window))

    processed_buttons = set()

    for area_name, area_widget in search_areas:
        try:
            collapsible_buttons = area_widget.findChildren(ctk.ctkCollapsibleButton)

            for button in collapsible_buttons:
                # Avoid processing the same button twice
                button_id = id(button)
                if button_id in processed_buttons:
                    continue
                processed_buttons.add(button_id)

                button_text = button.text if hasattr(button, 'text') else ""
                if callable(button_text):
                    button_text = button_text()

                # Check if we should expand this section
                should_expand = any(pattern in button_text for pattern in expand)
                should_collapse = any(pattern in button_text for pattern in collapse)

                if should_expand and not should_collapse:
                    button.collapsed = False
                    logger.info(f"Expanded: {button_text}")
                elif should_collapse:
                    button.collapsed = True
                    logger.info(f"Collapsed: {button_text}")

        except Exception as e:
            logger.warning(f"Could not configure sections in {area_name}: {e}")

    qt.QApplication.processEvents()


def capture_main_ui(output_dir: Path | str | None = None) -> Path | None:
    """Capture the main MouseMaster UI screenshot.

    This is the primary screenshot for Extension Index submission.
    Shows the module panel with MouseMaster controls in context of Slicer.

    Args:
        output_dir: Directory to save screenshot (default: Screenshots/)

    Returns:
        Path to saved screenshot, or None if failed
    """
    import qt

    output_dir = Path(output_dir) if output_dir else get_screenshot_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Set up clean UI state with 3D-only layout (cleaner than slice views)
    setup_clean_ui(layout="3d_only")

    # Ensure module is visible
    if not ensure_mousemaster_visible():
        return None

    # Configure sections: expand useful ones, collapse developer/unneeded ones
    configure_module_sections(
        expand=["Button Mappings", "Mouse Selection", "Preset Management"],
        collapse=["Reload", "Help", "Data Probe"]
    )

    # Wait for UI to settle
    qt.QApplication.processEvents()

    # Give a bit more time for UI to render
    import time
    time.sleep(0.5)
    qt.QApplication.processEvents()

    # Capture main window with module visible
    filepath = output_dir / "main-ui.png"

    if capture_main_window(filepath, size=(1200, 800)):
        print(f"✓ Captured main UI: {filepath}")
        return filepath
    return None


def capture_button_mapping(output_dir: Path | str | None = None) -> Path | None:
    """Capture the button mapping table - the main module panel screenshot.

    This is the clearest view of the MouseMaster functionality,
    ideal for documentation and Extension Index submission.

    Args:
        output_dir: Directory to save screenshot

    Returns:
        Path to saved screenshot, or None if failed
    """
    import qt

    output_dir = Path(output_dir) if output_dir else get_screenshot_dir()

    # Set up clean UI
    setup_clean_ui(layout="3d_only")

    if not ensure_mousemaster_visible():
        return None

    # Configure sections for a clean, user-focused view
    configure_module_sections(
        expand=["Button Mappings", "Mouse Selection", "Preset Management"],
        collapse=["Reload", "Help", "Data Probe"]
    )

    import time
    time.sleep(0.3)
    qt.QApplication.processEvents()

    filepath = output_dir / "button-mapping.png"

    if capture_module_panel(filepath):
        print(f"✓ Captured button mapping: {filepath}")
        return filepath
    return None


def capture_preset_selector(output_dir: Path | str | None = None) -> Path | None:
    """Capture the module panel focused on preset selection.

    Shows the preset management section for documentation.

    Args:
        output_dir: Directory to save screenshot

    Returns:
        Path to saved screenshot, or None if failed
    """
    import qt

    output_dir = Path(output_dir) if output_dir else get_screenshot_dir()

    # Set up clean UI
    setup_clean_ui(layout="3d_only")

    if not ensure_mousemaster_visible():
        return None

    # Focus on preset management - collapse Button Mappings to show preset section
    configure_module_sections(
        expand=["Mouse Selection", "Preset Management"],
        collapse=["Reload", "Help", "Button Mappings", "Data Probe"]
    )

    import time
    time.sleep(0.3)
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
        "main-ui.png": "MouseMaster module in 3D Slicer showing button mapping configuration",
        "button-mapping.png": "Module panel with button mapping table for action assignments",
        "preset-selector.png": "Mouse model and preset selection interface",
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
