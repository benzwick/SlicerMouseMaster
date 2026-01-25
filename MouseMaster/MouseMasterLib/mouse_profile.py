"""Mouse profile definitions.

This module provides dataclasses for representing mouse hardware profiles,
including button definitions and device features.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class MouseButton:
    """Represents a single mouse button.

    Attributes:
        id: Unique identifier for the button (e.g., "left", "back", "thumb")
        name: Human-readable button name
        qt_button: Qt button code for this button
        remappable: Whether this button can be remapped
        default_action: Optional default action ID for this button
    """

    id: str
    name: str
    qt_button: int
    remappable: bool = True
    default_action: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MouseButton:
        """Create a MouseButton from a dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            qt_button=data["qtButton"],
            remappable=data.get("remappable", True),
            default_action=data.get("defaultAction"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "qtButton": self.qt_button,
            "remappable": self.remappable,
        }
        if self.default_action:
            result["defaultAction"] = self.default_action
        return result


@dataclass
class MouseFeatures:
    """Optional mouse features.

    Attributes:
        horizontal_scroll: Whether mouse has horizontal scroll
        thumb_wheel: Whether mouse has a thumb wheel
        gesture_button: Whether mouse has a gesture button
    """

    horizontal_scroll: bool = False
    thumb_wheel: bool = False
    gesture_button: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MouseFeatures:
        """Create MouseFeatures from a dictionary."""
        return cls(
            horizontal_scroll=data.get("horizontalScroll", False),
            thumb_wheel=data.get("thumbWheel", False),
            gesture_button=data.get("gestureButton", False),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "horizontalScroll": self.horizontal_scroll,
            "thumbWheel": self.thumb_wheel,
            "gestureButton": self.gesture_button,
        }


@dataclass
class MouseProfile:
    """Represents a mouse hardware profile.

    A profile defines the buttons and features available on a specific
    mouse model, allowing MouseMaster to provide appropriate configuration
    options.

    Attributes:
        id: Unique identifier (e.g., "logitech_mx_master_3s")
        name: Human-readable name (e.g., "Logitech MX Master 3S")
        vendor: Vendor name
        vendor_id: USB vendor ID (hex string)
        product_ids: List of USB product IDs (hex strings)
        buttons: List of button definitions
        features: Optional feature flags
    """

    id: str
    name: str
    vendor: str
    vendor_id: str
    product_ids: list[str]
    buttons: list[MouseButton]
    features: MouseFeatures = field(default_factory=MouseFeatures)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MouseProfile:
        """Create a MouseProfile from a dictionary."""
        buttons = [MouseButton.from_dict(b) for b in data.get("buttons", [])]
        features = MouseFeatures.from_dict(data.get("features", {}))

        return cls(
            id=data["id"],
            name=data["name"],
            vendor=data.get("vendor", "Unknown"),
            vendor_id=data.get("vendorId", "0x0000"),
            product_ids=data.get("productIds", []),
            buttons=buttons,
            features=features,
        )

    @classmethod
    def from_json_file(cls, path: Path | str) -> MouseProfile:
        """Load a MouseProfile from a JSON file.

        Args:
            path: Path to the JSON file

        Returns:
            Loaded MouseProfile

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is invalid
            KeyError: If required fields are missing
        """
        path = Path(path)
        logger.debug(f"Loading mouse profile from {path}")

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "vendor": self.vendor,
            "vendorId": self.vendor_id,
            "productIds": self.product_ids,
            "buttons": [b.to_dict() for b in self.buttons],
            "features": self.features.to_dict(),
        }

    def to_json_file(self, path: Path | str) -> None:
        """Save the profile to a JSON file.

        Args:
            path: Path to save the JSON file
        """
        path = Path(path)
        logger.debug(f"Saving mouse profile to {path}")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    def get_button(self, button_id: str) -> MouseButton | None:
        """Get a button by ID.

        Args:
            button_id: The button ID to find

        Returns:
            The MouseButton if found, None otherwise
        """
        for button in self.buttons:
            if button.id == button_id:
                return button
        return None

    def get_button_by_qt_code(self, qt_button: int) -> MouseButton | None:
        """Get a button by Qt button code.

        Args:
            qt_button: The Qt button code

        Returns:
            The MouseButton if found, None otherwise
        """
        for button in self.buttons:
            if button.qt_button == qt_button:
                return button
        return None

    def get_remappable_buttons(self) -> list[MouseButton]:
        """Get all remappable buttons.

        Returns:
            List of buttons that can be remapped
        """
        return [b for b in self.buttons if b.remappable]

    @property
    def button_count(self) -> int:
        """Get the total number of buttons."""
        return len(self.buttons)

    @property
    def remappable_count(self) -> int:
        """Get the number of remappable buttons."""
        return len(self.get_remappable_buttons())
