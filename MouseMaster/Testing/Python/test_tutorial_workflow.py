#!/usr/bin/env python
"""Tutorial workflow test - generates living documentation.

This test runs through the segmentation workflow tutorial, capturing
screenshots at each step. The screenshots and test output are used
to generate up-to-date documentation.

Run in Slicer:
    Slicer --python-script MouseMaster/Testing/Python/test_tutorial_workflow.py

The test:
1. Loads sample data (MRHead)
2. Opens MouseMaster module
3. Configures mouse and preset
4. Opens Segment Editor
5. Demonstrates button mappings
6. Captures screenshots at each step
7. Generates tutorial documentation
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path


def get_output_dir() -> Path:
    """Get output directory for tutorial artifacts."""
    import os

    workspace = os.environ.get("GITHUB_WORKSPACE")
    if workspace:
        return Path(workspace) / "docs" / "user-guide" / "_generated"

    return Path(__file__).parent.parent.parent.parent / "docs" / "user-guide" / "_generated"


def run_tutorial() -> dict:
    """Run the tutorial workflow and capture screenshots.

    Returns:
        dict with steps, screenshots, and metadata
    """
    import slicer

    output_dir = get_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Import screenshot capture
    sys.path.insert(0, str(Path(__file__).parent))
    from screenshot_capture import ScreenshotCapture

    capture = ScreenshotCapture(base_folder=output_dir)
    capture.set_group("tutorial")

    results = {
        "timestamp": datetime.now().isoformat(),
        "steps": [],
        "screenshots": [],
        "success": True,
        "errors": [],
    }

    def step(name: str, description: str):
        """Record a tutorial step."""
        results["steps"].append({"name": name, "description": description})
        print(f"\n=== Step: {name} ===")
        print(description)

    try:
        # Step 1: Load Sample Data
        step(
            "Load Sample Data",
            "Load MRHead from Sample Data module for segmentation practice.",
        )
        slicer.util.selectModule("SampleData")
        slicer.app.processEvents()
        capture.capture_layout("01_sample_data_module")

        import SampleData

        volume_node = SampleData.SampleDataLogic().downloadMRHead()
        slicer.app.processEvents()
        capture.capture_layout("02_mrhead_loaded")
        results["steps"][-1]["data"] = {"volume": volume_node.GetName()}

        # Step 2: Open MouseMaster
        step(
            "Open MouseMaster",
            "Navigate to Modules > Utilities > MouseMaster.",
        )
        slicer.util.selectModule("MouseMaster")
        slicer.app.processEvents()
        capture.capture_layout("03_mousemaster_module")
        capture.capture_module_widget("04_mousemaster_panel")

        # Step 3: Select Mouse
        step(
            "Select Mouse",
            "Choose your mouse model from the dropdown. Select Generic 3-Button if not listed.",
        )
        widget = slicer.modules.mousemaster.widgetRepresentation().self()

        # Select a mouse (Generic 3-Button for tutorial)
        for i in range(widget.mouseSelector.count):
            if "Generic 3-Button" in widget.mouseSelector.itemText(i):
                widget.mouseSelector.setCurrentIndex(i)
                break
        slicer.app.processEvents()
        capture.capture_module_widget("05_mouse_selected")
        results["steps"][-1]["data"] = {"mouse": widget.mouseSelector.currentText}

        # Step 4: Select Preset
        step(
            "Select Preset",
            "Choose a preset configuration for your workflow.",
        )
        # Select first available preset
        if widget.presetSelector.count > 1:
            widget.presetSelector.setCurrentIndex(1)
        slicer.app.processEvents()
        capture.capture_module_widget("06_preset_selected")
        results["steps"][-1]["data"] = {"preset": widget.presetSelector.currentText}

        # Step 5: Review Button Mappings
        step(
            "Review Button Mappings",
            "Expand Button Mappings to see current configuration.",
        )
        # Mappings should auto-expand when preset selected
        slicer.app.processEvents()
        capture.capture_module_widget("07_button_mappings")

        # Capture mapping table info
        mappings = []
        table = widget.mappingTable
        row_count = table.rowCount
        if callable(row_count):
            row_count = row_count()
        for row in range(row_count):
            button_item = table.item(row, 0)
            action_widget = table.cellWidget(row, 1)
            if button_item and action_widget:
                mappings.append({
                    "button": button_item.text(),
                    "action": action_widget.currentText if hasattr(action_widget, 'currentText') else str(action_widget),
                })
        results["steps"][-1]["data"] = {"mappings": mappings}

        # Step 6: Enable MouseMaster
        step(
            "Enable MouseMaster",
            "Click Enable Mouse Master to activate button remapping.",
        )
        if widget.enableButton.enabled:
            widget.enableButton.setChecked(True)
            slicer.app.processEvents()
        capture.capture_module_widget("08_enabled")
        results["steps"][-1]["data"] = {"enabled": widget.enableButton.checked}

        # Step 7: Open Segment Editor
        step(
            "Open Segment Editor",
            "Go to Segment Editor to test mappings with segmentation workflow.",
        )
        slicer.util.selectModule("SegmentEditor")
        slicer.app.processEvents()
        capture.capture_layout("09_segment_editor")

        # Create a segmentation
        segmentation_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
        segmentation_node.CreateDefaultDisplayNodes()
        segmentation_node.SetReferenceImageGeometryParameterFromVolumeNode(volume_node)

        # Get segment editor widget
        segment_editor = slicer.modules.segmenteditor.widgetRepresentation().self()
        segment_editor.editor.setSegmentationNode(segmentation_node)
        segment_editor.editor.setSourceVolumeNode(volume_node)
        slicer.app.processEvents()

        # Add a segment
        segmentation_node.GetSegmentation().AddEmptySegment("Brain")
        slicer.app.processEvents()
        capture.capture_layout("10_segment_created")

        # Step 8: Test Complete
        step(
            "Test Your Mappings",
            "Press your mapped buttons to verify they work. Back=Undo, Forward=Redo.",
        )
        capture.capture_layout("11_tutorial_complete")

        # Disable MouseMaster for cleanup
        slicer.util.selectModule("MouseMaster")
        widget = slicer.modules.mousemaster.widgetRepresentation().self()
        widget.enableButton.setChecked(False)
        slicer.app.processEvents()

    except Exception as e:
        import traceback

        results["success"] = False
        results["errors"].append(str(e))
        print(f"ERROR: {e}")
        traceback.print_exc()

        import contextlib
        with contextlib.suppress(Exception):
            capture.capture_layout(f"error_{len(results['errors'])}")

    # Save manifest
    capture.save_manifest()

    # Save results
    results_file = output_dir / "tutorial_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    # Generate RST documentation
    generate_tutorial_rst(results, output_dir)

    print("\n" + "=" * 60)
    print("TUTORIAL TEST COMPLETE")
    print("=" * 60)
    print(f"Steps completed: {len(results['steps'])}")
    print(f"Success: {results['success']}")
    print(f"Output: {output_dir}")

    return results


def generate_tutorial_rst(results: dict, output_dir: Path) -> None:
    """Generate RST documentation from test results."""
    rst_file = output_dir.parent / "tutorial.rst"

    lines = [
        "Tutorial: Segmentation Workflow",
        "=" * 31,
        "",
        ".. note::",
        "",
        f"   This tutorial was auto-generated from test run on {results['timestamp'][:10]}.",
        "   Screenshots reflect the actual current UI.",
        "",
    ]

    for i, step in enumerate(results["steps"], 1):
        lines.append(f"Step {i}: {step['name']}")
        lines.append("-" * (len(f"Step {i}: {step['name']}")))
        lines.append("")
        lines.append(step["description"])
        lines.append("")

        # Add screenshot if exists
        lines.append(f".. image:: _generated/{i:02d}*.png")
        lines.append("   :width: 100%")
        lines.append("")

        # Add data if present
        if "data" in step and "mappings" in step["data"]:
            lines.append("Current mappings:")
            lines.append("")
            for m in step["data"]["mappings"]:
                lines.append(f"- **{m['button']}**: {m['action']}")
            lines.append("")

        lines.append("")

    with open(rst_file, "w") as f:
        f.write("\n".join(lines))

    print(f"Generated: {rst_file}")


if __name__ == "__main__":
    results = run_tutorial()
    sys.exit(0 if results["success"] else 1)
