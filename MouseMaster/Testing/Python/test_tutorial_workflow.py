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
        capture.capture_layout("05_mouse_selected")
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
        capture.capture_layout("06_preset_selected")
        results["steps"][-1]["data"] = {"preset": widget.presetSelector.currentText}

        # Step 5: Review Button Mappings
        step(
            "Review Button Mappings",
            "Expand Button Mappings to see current configuration.",
        )
        # Mappings should auto-expand when preset selected
        slicer.app.processEvents()

        # Capture full layout showing mapping table with context
        capture.capture_layout("07_button_mappings")

        # Also capture just the module widget for detail view
        capture.capture_module_widget("08_button_mappings_detail")

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
                mappings.append(
                    {
                        "button": button_item.text(),
                        "action": action_widget.currentText
                        if hasattr(action_widget, "currentText")
                        else str(action_widget),
                    }
                )
        results["steps"][-1]["data"] = {"mappings": mappings}

        # Step 6: Enable MouseMaster
        step(
            "Enable MouseMaster",
            "Click Enable Mouse Master to activate button remapping.",
        )
        # Capture before enabling
        capture.capture_module_widget("09_before_enable")

        if widget.enableButton.enabled:
            widget.enableButton.setChecked(True)
            slicer.app.processEvents()

        # Capture after enabling - full layout shows active status
        capture.capture_layout("10_enabled")
        capture.capture_module_widget("11_enabled_detail")
        results["steps"][-1]["data"] = {"enabled": widget.enableButton.checked}

        # Step 7: Open Segment Editor
        step(
            "Open Segment Editor",
            "Go to Segment Editor to test mappings with segmentation workflow.",
        )
        slicer.util.selectModule("SegmentEditor")
        slicer.app.processEvents()
        capture.capture_layout("12_segment_editor")

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
        capture.capture_layout("13_segment_created")

        # Step 8: Test Complete
        step(
            "Test Your Mappings",
            "Press your mapped buttons to verify they work. Back=Undo, Forward=Redo.",
        )
        capture.capture_layout("14_tutorial_complete")

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

    # Map step indices to screenshot filenames based on manifest
    manifest_file = output_dir / "manifest.json"
    screenshot_map = {}
    if manifest_file.exists():
        with open(manifest_file) as f:
            manifest = json.load(f)
            for s in manifest.get("screenshots", []):
                # Extract step number from description like "02_mrhead_loaded"
                desc = s.get("description", "")
                if desc and desc[0:2].isdigit():
                    step_num = int(desc[0:2])
                    screenshot_map[step_num] = s["filename"]

    lines = [
        "Tutorial: Segmentation Workflow",
        "================================",
        "",
        "This hands-on tutorial walks through a complete segmentation workflow",
        "using MouseMaster to streamline your mouse button mappings.",
        "",
        "Prerequisites",
        "-------------",
        "",
        "- 3D Slicer installed with MouseMaster extension",
        "- A multi-button mouse (or use Generic 3-Button profile)",
        "",
    ]

    # Screenshot number tracking based on captured files
    screenshot_num = 1

    for i, step_data in enumerate(results["steps"], 1):
        step_name = step_data["name"]
        lines.append(f"Step {i}: {step_name}")
        lines.append("-" * (len(f"Step {i}: {step_name}")))
        lines.append("")
        lines.append(step_data["description"])
        lines.append("")

        # Find matching screenshot(s) for this step
        # Screenshots are numbered sequentially, multiple per step possible
        step_screenshots = []
        for num, filename in screenshot_map.items():
            # Match screenshots that start with step number pattern
            if num == screenshot_num or (num > screenshot_num and num <= screenshot_num + 2):
                step_screenshots.append(filename)

        if step_screenshots:
            # Use the last screenshot for this step (most complete state)
            screenshot = step_screenshots[-1]
            lines.append(f".. figure:: _generated/{screenshot}")
            lines.append("   :width: 100%")
            lines.append(f"   :alt: {step_name}")
            lines.append("")
            screenshot_num = int(screenshot[:3]) + 1

        # Add contextual data if present
        if "data" in step_data:
            data = step_data["data"]

            if "volume" in data:
                lines.append(f"*Loaded volume: {data['volume']}*")
                lines.append("")

            if "mouse" in data:
                lines.append(f"*Selected mouse: {data['mouse']}*")
                lines.append("")

            if "preset" in data:
                lines.append(f"*Applied preset: {data['preset']}*")
                lines.append("")

            if data.get("mappings"):
                lines.append("**Current button mappings:**")
                lines.append("")
                for m in data["mappings"]:
                    lines.append(f"- **{m['button']}** → {m['action']}")
                lines.append("")

            if "enabled" in data:
                status = "active" if data["enabled"] else "inactive"
                lines.append(f"*MouseMaster status: {status}*")
                lines.append("")

        lines.append("")

    # Add next steps section
    lines.extend(
        [
            "What's Next?",
            "------------",
            "",
            "Now that you've completed the basic workflow:",
            "",
            "- :doc:`button-mapping` - Customize your button assignments",
            "- :doc:`presets` - Save and share your configurations",
            "- :doc:`context-bindings` - Create module-specific mappings",
            "",
            "Tips",
            "----",
            "",
            "- Use **Back/Forward** buttons for Undo/Redo in any module",
            "- Create module-specific bindings for Segment Editor effects",
            "- Export your presets to share with colleagues",
            "",
            "----",
            "",
            f"*This tutorial was auto-generated on {results['timestamp'][:10]}.*",
            "*Screenshots reflect the current UI.*",
            "",
        ]
    )

    with open(rst_file, "w") as f:
        f.write("\n".join(lines))

    print(f"Generated: {rst_file}")


if __name__ == "__main__":
    results = run_tutorial()
    sys.exit(0 if results["success"] else 1)
