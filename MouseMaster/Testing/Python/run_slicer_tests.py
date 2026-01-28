#!/usr/bin/env python
"""Run MouseMaster integration tests inside Slicer with screenshot capture.

This script is designed to run both locally and in CI:

Local usage (in Slicer Python console):
    exec(open('/path/to/run_slicer_tests.py').read())

CI usage:
    Slicer --python-script MouseMaster/Testing/Python/run_slicer_tests.py

The script:
1. Loads the MouseMaster module
2. Runs the widget interaction tests
3. Captures screenshots at each step
4. Generates a manifest.json for Claude Code review
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path


def get_screenshots_dir() -> Path:
    """Get the screenshots output directory."""
    # Check for CI environment
    import os
    workspace = os.environ.get('GITHUB_WORKSPACE')
    if workspace:
        return Path(workspace) / 'test-results' / 'screenshots'

    # Local: use Testing/Python/screenshots
    return Path(__file__).parent / 'screenshots'


def run_tests():
    """Run the MouseMaster integration tests with screenshots."""
    import slicer

    screenshots_dir = get_screenshots_dir()
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    # Import screenshot capture utility
    sys.path.insert(0, str(Path(__file__).parent))
    from screenshot_capture import ScreenshotCapture

    capture = ScreenshotCapture(base_folder=screenshots_dir)
    results = {'passed': 0, 'failed': 0, 'errors': []}

    print(f"Screenshots will be saved to: {screenshots_dir}")
    print("=" * 60)

    try:
        # Wait for Slicer to initialize
        slicer.app.processEvents()

        # Load MouseMaster module
        print("Loading MouseMaster module...")
        slicer.util.selectModule('MouseMaster')
        slicer.app.processEvents()

        capture.set_group("integration_tests")
        capture.capture_layout("Initial Slicer layout with MouseMaster")

        # Get the widget
        widget_rep = slicer.modules.mousemaster.widgetRepresentation()
        if not widget_rep:
            raise RuntimeError("MouseMaster widget not available")

        widget = widget_rep.self()
        capture.capture_module_widget("MouseMaster module initial state")

        # Run test: Mouse selector
        print("\nTest: Mouse selector...")
        try:
            if hasattr(widget, 'mouseSelector') and widget.mouseSelector.count > 1:
                widget.mouseSelector.setCurrentIndex(1)
                slicer.app.processEvents()
                capture.capture_module_widget("After selecting mouse")
                print("  PASSED: Mouse selector works")
                results['passed'] += 1
            else:
                print("  SKIPPED: No mice available")
        except Exception as e:
            print(f"  FAILED: {e}")
            results['failed'] += 1
            results['errors'].append(f"Mouse selector: {e}")

        # Run test: Preset selector
        print("\nTest: Preset selector...")
        try:
            if hasattr(widget, 'presetSelector') and widget.presetSelector.count > 1:
                widget.presetSelector.setCurrentIndex(1)
                slicer.app.processEvents()
                capture.capture_module_widget("After selecting preset")
                print("  PASSED: Preset selector works")
                results['passed'] += 1
            else:
                print("  SKIPPED: No presets available")
        except Exception as e:
            print(f"  FAILED: {e}")
            results['failed'] += 1
            results['errors'].append(f"Preset selector: {e}")

        # Run test: Context toggle
        print("\nTest: Context toggle...")
        try:
            if hasattr(widget, 'contextToggle'):
                initial_state = widget.contextToggle.checked
                widget.contextToggle.setChecked(True)
                slicer.app.processEvents()
                capture.capture_module_widget("Context toggle enabled")

                widget.contextToggle.setChecked(initial_state)
                slicer.app.processEvents()
                print("  PASSED: Context toggle works")
                results['passed'] += 1
            else:
                print("  SKIPPED: No context toggle")
        except Exception as e:
            print(f"  FAILED: {e}")
            results['failed'] += 1
            results['errors'].append(f"Context toggle: {e}")

        # Run test: Enable button
        print("\nTest: Enable button...")
        try:
            if hasattr(widget, 'enableButton'):
                capture.capture_widget(widget.enableButton, "Enable button state")
                print("  PASSED: Enable button accessible")
                results['passed'] += 1
            else:
                print("  SKIPPED: No enable button")
        except Exception as e:
            print(f"  FAILED: {e}")
            results['failed'] += 1
            results['errors'].append(f"Enable button: {e}")

        # Run test: Mapping table
        print("\nTest: Mapping table...")
        try:
            if hasattr(widget, 'mappingTable'):
                capture.capture_widget(widget.mappingTable, "Mapping table")
                print(f"  PASSED: Mapping table has {widget.mappingTable.rowCount()} rows")
                results['passed'] += 1
            else:
                print("  SKIPPED: No mapping table")
        except Exception as e:
            print(f"  FAILED: {e}")
            results['failed'] += 1
            results['errors'].append(f"Mapping table: {e}")

        # Capture final state
        capture.capture_layout("Final layout after all tests")

        # Save manifest
        capture.save_manifest()

        # Also run the built-in module tests
        print("\n" + "=" * 60)
        print("Running MouseMaster built-in tests...")
        import MouseMaster
        test = MouseMaster.MouseMasterTest()
        builtin_success = test.runTest()
        if builtin_success:
            print("Built-in tests: PASSED")
            results['passed'] += 1
        else:
            print("Built-in tests: FAILED")
            results['failed'] += 1

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        results['failed'] += 1
        results['errors'].append(str(e))

        # Capture error state screenshot
        try:
            capture.capture_layout(f"Error state: {e}")
            capture.save_manifest()
        except Exception as capture_error:
            print(f"Failed to capture error screenshot: {capture_error}")

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    if results['errors']:
        print("\nErrors:")
        for err in results['errors']:
            print(f"  - {err}")

    # Write results file
    results_file = screenshots_dir.parent / 'test-results.json' if screenshots_dir.parent.name == 'screenshots' else screenshots_dir / 'test-results.json'
    results_file = screenshots_dir.parent / 'test-results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'passed': results['passed'],
            'failed': results['failed'],
            'errors': results['errors'],
            'screenshots_dir': str(screenshots_dir),
        }, f, indent=2)
    print(f"\nResults saved to: {results_file}")

    return results['failed'] == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
