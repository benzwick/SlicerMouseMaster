"""Screenshot capture utility for MouseMaster visual testing.

This module provides screenshot capture functionality for tests running inside Slicer.
Screenshots are saved with auto-numbering and a manifest.json for Claude Code review.

Usage:
    from screenshot_capture import ScreenshotCapture

    capture = ScreenshotCapture(base_folder=Path("./screenshots"))
    capture.set_group("widget_test")
    capture.capture_layout("Initial state")
    capture.capture_widget(widget, "Mouse selector dropdown")
    capture.save_manifest()
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


@dataclass
class ScreenshotInfo:
    """Information about a captured screenshot."""

    filename: str
    description: str
    group: str
    timestamp: str
    capture_type: str  # "layout", "slice_view", "3d_view", "widget"
    metadata: dict[str, Any] = field(default_factory=dict)


class ScreenshotCapture:
    """Capture screenshots during Slicer testing for visual review.

    This class provides methods to capture:
    - Full layout screenshots
    - Individual slice view screenshots
    - 3D view screenshots
    - Specific widget screenshots

    All screenshots are auto-numbered and a manifest.json is generated
    with descriptions for each screenshot, enabling Claude Code to review
    the visual state of the application during testing.
    """

    def __init__(
        self,
        base_folder: Path | str = Path("./screenshots"),
        flat_mode: bool = True,
    ):
        """Initialize screenshot capture.

        Args:
            base_folder: Directory to save screenshots
            flat_mode: If True, save all screenshots in base_folder with numbered names.
                      If False, create subdirectories per group.
        """
        self.base_folder = Path(base_folder)
        self.flat_mode = flat_mode
        self._counter = 0
        self._current_group = "default"
        self._screenshots: list[ScreenshotInfo] = []
        self._slicer_available = False

        # Check if we're running inside real Slicer
        try:
            from unittest.mock import MagicMock

            import slicer

            self._slicer_available = (
                hasattr(slicer, "mrmlScene")
                and not isinstance(slicer.mrmlScene, MagicMock)
                and hasattr(slicer, "app")
                and not isinstance(slicer.app, MagicMock)
            )
        except ImportError:
            self._slicer_available = False

    @property
    def is_available(self) -> bool:
        """Check if screenshot capture is available (running in Slicer)."""
        return self._slicer_available

    def set_group(self, group_name: str) -> None:
        """Set the current screenshot group.

        Groups help organize screenshots by test or workflow.

        Args:
            group_name: Name of the screenshot group
        """
        self._current_group = group_name

    def _get_output_path(self) -> Path:
        """Get the output directory for current group."""
        if self.flat_mode:
            return self.base_folder
        return self.base_folder / self._current_group

    def _next_filename(self, description: str = "") -> str:
        """Generate next auto-numbered filename with description.

        Args:
            description: Description to include in filename (sanitized)

        Returns:
            Filename like "001_step1_data_loaded.png"
        """
        self._counter += 1
        # Sanitize description for filename: lowercase, replace spaces/special chars with underscore
        if description:
            safe_desc = description.lower()
            safe_desc = "".join(c if c.isalnum() else "_" for c in safe_desc)
            safe_desc = "_".join(
                part for part in safe_desc.split("_") if part
            )  # Remove empty parts
            safe_desc = safe_desc[:50]  # Limit length
            return f"{self._counter:03d}_{safe_desc}.png"
        if self.flat_mode:
            return f"{self._counter:03d}.png"
        return f"{self._current_group}_{self._counter:03d}.png"

    def _ensure_output_dir(self) -> Path:
        """Ensure output directory exists."""
        output_dir = self._get_output_path()
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def capture_layout(
        self, description: str, metadata: dict[str, Any] | None = None
    ) -> ScreenshotInfo | None:
        """Capture the full Slicer layout.

        Args:
            description: Description of what this screenshot shows
            metadata: Optional additional metadata

        Returns:
            ScreenshotInfo if captured, None if Slicer not available
        """
        if not self._slicer_available:
            return None

        import slicer

        output_dir = self._ensure_output_dir()
        filename = self._next_filename(description)
        filepath = output_dir / filename

        # Capture the layout
        slicer.util.mainWindow().grab().save(str(filepath))

        info = ScreenshotInfo(
            filename=filename,
            description=description,
            group=self._current_group,
            timestamp=datetime.now().isoformat(),
            capture_type="layout",
            metadata=metadata or {},
        )
        self._screenshots.append(info)
        return info

    def capture_slice_view(
        self,
        view_name: str,
        description: str,
        metadata: dict[str, Any] | None = None,
    ) -> ScreenshotInfo | None:
        """Capture a specific slice view.

        Args:
            view_name: Name of the slice view (e.g., "Red", "Green", "Yellow")
            description: Description of what this screenshot shows
            metadata: Optional additional metadata

        Returns:
            ScreenshotInfo if captured, None if not available
        """
        if not self._slicer_available:
            return None

        import slicer

        output_dir = self._ensure_output_dir()
        full_description = f"{view_name}_{description}"
        filename = self._next_filename(full_description)
        filepath = output_dir / filename

        layout_manager = slicer.app.layoutManager()
        if layout_manager:
            slice_widget = layout_manager.sliceWidget(view_name)
            if slice_widget:
                slice_widget.grab().save(str(filepath))

        info = ScreenshotInfo(
            filename=filename,
            description=f"[{view_name}] {description}",
            group=self._current_group,
            timestamp=datetime.now().isoformat(),
            capture_type="slice_view",
            metadata={"view_name": view_name, **(metadata or {})},
        )
        self._screenshots.append(info)
        return info

    def capture_3d_view(
        self,
        view_index: int = 0,
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ScreenshotInfo | None:
        """Capture a 3D view.

        Args:
            view_index: Index of the 3D view (usually 0)
            description: Description of what this screenshot shows
            metadata: Optional additional metadata

        Returns:
            ScreenshotInfo if captured, None if not available
        """
        if not self._slicer_available:
            return None

        import slicer

        output_dir = self._ensure_output_dir()
        full_description = f"3d_{view_index}_{description}"
        filename = self._next_filename(full_description)
        filepath = output_dir / filename

        layout_manager = slicer.app.layoutManager()
        if layout_manager:
            three_d_widget = layout_manager.threeDWidget(view_index)
            if three_d_widget:
                three_d_widget.grab().save(str(filepath))

        info = ScreenshotInfo(
            filename=filename,
            description=f"[3D-{view_index}] {description}",
            group=self._current_group,
            timestamp=datetime.now().isoformat(),
            capture_type="3d_view",
            metadata={"view_index": view_index, **(metadata or {})},
        )
        self._screenshots.append(info)
        return info

    def capture_widget(
        self,
        widget: Any,
        description: str,
        metadata: dict[str, Any] | None = None,
    ) -> ScreenshotInfo | None:
        """Capture a specific Qt widget.

        Args:
            widget: The Qt widget to capture
            description: Description of what this screenshot shows
            metadata: Optional additional metadata

        Returns:
            ScreenshotInfo if captured, None if not available
        """
        if not self._slicer_available:
            return None

        if widget is None:
            return None

        output_dir = self._ensure_output_dir()
        filename = self._next_filename(description)
        filepath = output_dir / filename

        # Capture the widget
        widget.grab().save(str(filepath))

        widget_class = type(widget).__name__
        info = ScreenshotInfo(
            filename=filename,
            description=description,
            group=self._current_group,
            timestamp=datetime.now().isoformat(),
            capture_type="widget",
            metadata={"widget_class": widget_class, **(metadata or {})},
        )
        self._screenshots.append(info)
        return info

    def capture_module_widget(
        self,
        description: str,
        metadata: dict[str, Any] | None = None,
    ) -> ScreenshotInfo | None:
        """Capture the MouseMaster module widget panel.

        Args:
            description: Description of what this screenshot shows
            metadata: Optional additional metadata

        Returns:
            ScreenshotInfo if captured, None if not available
        """
        if not self._slicer_available:
            return None

        import slicer

        try:
            module_widget = slicer.modules.MouseMasterWidget
            if module_widget and hasattr(module_widget, "parent"):
                return self.capture_widget(
                    module_widget.parent,
                    f"[MouseMaster] {description}",
                    metadata,
                )
        except AttributeError:
            pass

        return None

    def save_manifest(self) -> Path | None:
        """Save manifest.json with all screenshot information.

        The manifest provides descriptions and metadata for each screenshot,
        enabling Claude Code to understand what each screenshot shows.

        Returns:
            Path to manifest.json if saved, None otherwise
        """
        if not self._screenshots:
            return None

        output_dir = self._ensure_output_dir()
        manifest_path = output_dir / "manifest.json"

        manifest = {
            "generated": datetime.now().isoformat(),
            "total_screenshots": len(self._screenshots),
            "groups": list({s.group for s in self._screenshots}),
            "screenshots": [
                {
                    "filename": s.filename,
                    "description": s.description,
                    "group": s.group,
                    "timestamp": s.timestamp,
                    "capture_type": s.capture_type,
                    "metadata": s.metadata,
                }
                for s in self._screenshots
            ],
        }

        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        return manifest_path

    def reset(self) -> None:
        """Reset the capture state for a new test run."""
        self._counter = 0
        self._current_group = "default"
        self._screenshots = []


# Singleton instance for convenience
_default_capture: ScreenshotCapture | None = None


def get_screenshot_capture(base_folder: Path | str | None = None) -> ScreenshotCapture:
    """Get the default screenshot capture instance.

    Args:
        base_folder: Optional base folder override

    Returns:
        ScreenshotCapture instance
    """
    global _default_capture
    if _default_capture is None or base_folder is not None:
        folder = base_folder or Path(__file__).parent / "screenshots"
        _default_capture = ScreenshotCapture(base_folder=folder)
    return _default_capture
