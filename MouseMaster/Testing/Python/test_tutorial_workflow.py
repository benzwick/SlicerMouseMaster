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
        "success": True,
        "errors": [],
    }

    def step(name: str, description: str):
        """Record a tutorial step."""
        results["steps"].append({"name": name, "description": description, "screenshot": None})
        print(f"\n=== Step: {name} ===")
        print(description)

    def capture_step(description: str) -> str | None:
        """Capture screenshot for current step and store filename."""
        info = capture.capture_layout(description)
        if info:
            results["steps"][-1]["screenshot"] = info.filename
            return info.filename
        return None

    try:
        # ===========================================
        # SETUP: Resize window and panels for better screenshots
        # ===========================================
        main_window = slicer.util.mainWindow()
        main_window.resize(1920, 1080)
        slicer.app.processEvents()

        # Widen the module panel so content is readable
        import qt

        panel_dock_widget = main_window.findChildren(qt.QDockWidget, "PanelDockWidget")[0]
        main_window.resizeDocks([panel_dock_widget], [450], qt.Qt.Horizontal)
        slicer.app.processEvents()

        # Hide Python console to give more vertical space
        python_console = main_window.findChild(qt.QDockWidget, "PythonConsoleDockWidget")
        if python_console:
            python_console.setVisible(False)
        slicer.app.processEvents()

        # ===========================================
        # STEP 1: Load Sample Data
        # ===========================================
        step(
            "Load Sample Data",
            "Load MRHead from Sample Data module for segmentation practice.",
        )
        import SampleData

        volume_node = SampleData.SampleDataLogic().downloadMRHead()
        slicer.app.processEvents()

        # Use Four-Up layout to focus on the views (3D + 3 slices)
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)

        # Reset slice views to show the volume properly
        slicer.util.resetSliceViews()

        # Enable volume rendering with MR-Default preset for good brain visualization
        volRenLogic = slicer.modules.volumerendering.logic()
        displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volume_node)
        displayNode.SetVisibility(True)
        # Apply MR-Default preset for better MRI visualization
        preset = volRenLogic.GetPresetByName("MR-Default")
        if preset:
            displayNode.GetVolumePropertyNode().Copy(preset)

        # Reset 3D view camera to frame the volume
        threeDWidget = slicer.app.layoutManager().threeDWidget(0)
        threeDWidget.threeDView().resetFocalPoint()
        threeDWidget.threeDView().resetCamera()
        slicer.app.processEvents()

        # Hide module panel for this step to focus on the loaded data
        panel_dock_widget.setVisible(False)
        slicer.app.processEvents()

        capture_step("step1_data_loaded")
        results["steps"][-1]["data"] = {"volume": volume_node.GetName()}

        # Restore module panel for next steps
        panel_dock_widget.setVisible(True)
        slicer.app.processEvents()

        # ===========================================
        # STEP 2: Open MouseMaster
        # ===========================================
        step(
            "Open MouseMaster",
            "Navigate to Modules > Utilities > MouseMaster.",
        )

        # Switch to conventional layout for module-focused steps
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView)
        slicer.app.processEvents()

        slicer.util.selectModule("MouseMaster")
        slicer.app.processEvents()

        # Get widget reference
        widget = slicer.modules.mousemaster.widgetRepresentation().self()

        # Keep Button Mappings collapsed initially to show the module overview
        widget.mappingsCollapsible.collapsed = True
        slicer.app.processEvents()

        capture_step("step2_mousemaster")

        # ===========================================
        # STEP 3: Select Mouse (MX Master 3S)
        # ===========================================
        step(
            "Select Mouse",
            "Choose your mouse model from the dropdown. We'll use the Logitech MX Master 3S.",
        )

        # Select MX Master 3S - this has 4 remappable buttons
        mouse_found = False
        for i in range(widget.mouseSelector.count):
            if "MX Master 3S" in widget.mouseSelector.itemText(i):
                widget.mouseSelector.setCurrentIndex(i)
                mouse_found = True
                break

        # Fallback to Generic 5-Button if MX Master 3S not available
        if not mouse_found:
            for i in range(widget.mouseSelector.count):
                if "Generic 5-Button" in widget.mouseSelector.itemText(i):
                    widget.mouseSelector.setCurrentIndex(i)
                    break

        slicer.app.processEvents()

        # Now expand Button Mappings to show the change from step 2
        widget.mappingsCollapsible.collapsed = False
        slicer.app.processEvents()

        # Highlight the mouse selector dropdown
        capture_step("step3_mouse_selected")
        results["steps"][-1]["data"] = {"mouse": widget.mouseSelector.currentText}

        # ===========================================
        # STEP 4: Select Preset
        # ===========================================
        step(
            "Select Preset",
            "Choose a preset configuration for your workflow.",
        )

        # Select first available preset (index 1, after "-- Select Preset --")
        if widget.presetSelector.count > 1:
            widget.presetSelector.setCurrentIndex(1)
        slicer.app.processEvents()

        # Highlight the preset selector dropdown
        capture_step("step4_preset_selected")
        results["steps"][-1]["data"] = {"preset": widget.presetSelector.currentText}

        # ===========================================
        # STEP 5: Review Button Mappings
        # ===========================================
        step(
            "Review Button Mappings",
            "Review the button mappings for your mouse. The MX Master 3S has 4 remappable buttons.",
        )

        # Collect mapping data from the table
        mappings = []
        table = widget.mappingTable
        row_count = table.rowCount
        if callable(row_count):
            row_count = row_count()
        for row in range(row_count):
            button_item = table.item(row, 0)
            action_widget = table.cellWidget(row, 1)
            if button_item and action_widget:
                action_text = (
                    action_widget.currentText
                    if hasattr(action_widget, "currentText")
                    else str(action_widget)
                )
                mappings.append({"button": button_item.text(), "action": action_text})

        results["steps"][-1]["data"] = {"mappings": mappings}

        # Scroll the module panel to ensure mappings are visible
        # (already expanded from step 3)
        slicer.app.processEvents()

        # Highlight the mapping table
        capture_step("step5_button_mappings")

        # ===========================================
        # STEP 6: Enable MouseMaster
        # ===========================================
        step(
            "Enable MouseMaster",
            "Click Enable Mouse Master to activate button remapping.",
        )

        if widget.enableButton.enabled:
            widget.enableButton.setChecked(True)
            slicer.app.processEvents()

        # Highlight the enable button
        capture_step("step6_enabled")
        results["steps"][-1]["data"] = {"enabled": widget.enableButton.checked}

        # ===========================================
        # STEP 7: Open Segment Editor and Create Segment
        # ===========================================
        step(
            "Open Segment Editor",
            "Open Segment Editor and create a segment to start painting.",
        )

        slicer.util.selectModule("SegmentEditor")
        slicer.app.processEvents()

        # Create segmentation node
        segmentation_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
        segmentation_node.CreateDefaultDisplayNodes()
        segmentation_node.SetReferenceImageGeometryParameterFromVolumeNode(volume_node)

        # Set up segment editor
        segment_editor_widget = slicer.modules.segmenteditor.widgetRepresentation().self()
        segment_editor_widget.editor.setSegmentationNode(segmentation_node)
        segment_editor_widget.editor.setSourceVolumeNode(volume_node)
        slicer.app.processEvents()

        # Add a segment with a visible color
        segmentation_node.GetSegmentation().AddEmptySegment("Brain")
        slicer.app.processEvents()

        # Select Paint effect - this makes step 7 different from step 8
        segment_editor_widget.editor.setActiveEffectByName("Paint")
        slicer.app.processEvents()

        capture_step("step7_segment_editor")

        # ===========================================
        # STEP 8: Paint and Test Undo
        # ===========================================
        step(
            "Test Your Mappings",
            "Paint on the slice, then press Back button to Undo. Press Forward to Redo.",
        )

        # Actually paint something so we can demonstrate undo
        # Get the Paint effect and configure it
        effect = segment_editor_widget.editor.activeEffect()
        if effect:
            effect.setParameter("BrushSphere", "0")
            effect.setParameter("BrushDiameterMm", "15")
            slicer.app.processEvents()

        # Paint programmatically by using the effect's paint method
        # We'll paint at the center of the red slice view
        red_slice_widget = slicer.app.layoutManager().sliceWidget("Red")
        red_slice_node = red_slice_widget.mrmlSliceNode()

        # Get the center of the slice in RAS coordinates
        sliceToRAS = red_slice_node.GetSliceToRAS()
        center_ras = [
            sliceToRAS.GetElement(0, 3),
            sliceToRAS.GetElement(1, 3),
            sliceToRAS.GetElement(2, 3),
        ]

        # Use the segment editor effect to paint
        if effect:
            # Paint at a few positions to create visible stroke

            for offset in [0, 5, 10, 15, 20]:
                point_ras = [center_ras[0] + offset, center_ras[1], center_ras[2]]
                effect.self().paintApply(point_ras)

            slicer.app.processEvents()

        # Show 3D representation of segmentation
        segmentation_node.CreateClosedSurfaceRepresentation()
        slicer.app.processEvents()

        # Reset 3D view to show both volume and segmentation
        threeDWidget.threeDView().resetFocalPoint()
        slicer.app.processEvents()

        capture_step("step8_paint_test")

        # ===========================================
        # CLEANUP
        # ===========================================
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
        "================================",
        "",
        "This hands-on tutorial walks through a complete segmentation workflow",
        "using MouseMaster to streamline your mouse button mappings.",
        "",
        "Prerequisites",
        "-------------",
        "",
        "- 3D Slicer installed with MouseMaster extension",
        "- A multi-button mouse (this tutorial uses the Logitech MX Master 3S)",
        "",
    ]

    for i, step_data in enumerate(results["steps"], 1):
        step_name = step_data["name"]
        lines.append(f"Step {i}: {step_name}")
        lines.append("-" * (len(f"Step {i}: {step_name}")))
        lines.append("")
        lines.append(step_data["description"])
        lines.append("")

        # Use screenshot stored directly in step result
        filename = step_data.get("screenshot")
        if filename:
            lines.append(f".. figure:: _generated/{filename}")
            lines.append("   :width: 100%")
            lines.append(f"   :alt: {step_name}")
            lines.append("")

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
