"""Platform-specific adaptations for mouse handling.

This module provides abstractions for handling platform differences
in mouse button codes, modifier keys, and device detection.
"""

from __future__ import annotations

import logging
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum

logger = logging.getLogger(__name__)


class CanonicalButton(IntEnum):
    """Canonical button identifiers used internally.

    These are platform-independent button identifiers that all
    platform-specific codes are normalized to.
    """

    UNKNOWN = 0
    LEFT = 1
    RIGHT = 2
    MIDDLE = 4
    BACK = 8
    FORWARD = 16
    EXTRA1 = 32
    EXTRA2 = 64
    EXTRA3 = 128


# Mapping from canonical buttons to string IDs
BUTTON_ID_MAP: dict[CanonicalButton, str] = {
    CanonicalButton.LEFT: "left",
    CanonicalButton.RIGHT: "right",
    CanonicalButton.MIDDLE: "middle",
    CanonicalButton.BACK: "back",
    CanonicalButton.FORWARD: "forward",
    CanonicalButton.EXTRA1: "thumb",  # Button 32 - thumb button on MX Master etc.
    CanonicalButton.EXTRA2: "extra1",
    CanonicalButton.EXTRA3: "extra2",
}


class CanonicalModifier(IntEnum):
    """Canonical modifier key identifiers."""

    NONE = 0
    SHIFT = 1
    CTRL = 2
    ALT = 4
    META = 8


@dataclass
class NormalizedEvent:
    """A platform-normalized mouse event.

    Attributes:
        button: The canonical button
        button_id: String identifier for the button
        modifiers: Set of active modifiers
        x: X coordinate (if applicable)
        y: Y coordinate (if applicable)
    """

    button: CanonicalButton
    button_id: str
    modifiers: set[str]
    x: int = 0
    y: int = 0


class PlatformAdapter(ABC):
    """Abstract base class for platform-specific adapters.

    Subclasses implement platform-specific button code normalization
    and modifier key handling.
    """

    _instance: PlatformAdapter | None = None

    @classmethod
    def get_instance(cls) -> PlatformAdapter:
        """Get the platform-appropriate adapter instance.

        Returns:
            The singleton PlatformAdapter for the current platform
        """
        if cls._instance is None:
            if sys.platform == "win32":
                cls._instance = WindowsAdapter()
            elif sys.platform == "darwin":
                cls._instance = MacOSAdapter()
            else:
                cls._instance = LinuxAdapter()
            logger.info(f"Using platform adapter: {cls._instance.__class__.__name__}")
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton (for testing)."""
        cls._instance = None

    @abstractmethod
    def normalize_button(self, qt_button: int) -> CanonicalButton:
        """Convert a Qt button code to canonical form.

        Args:
            qt_button: The Qt button code (e.g., Qt.LeftButton)

        Returns:
            The canonical button enum value
        """

    @abstractmethod
    def normalize_modifiers(self, qt_modifiers: int) -> set[str]:
        """Convert Qt modifiers to canonical form.

        Args:
            qt_modifiers: Qt modifier flags

        Returns:
            Set of modifier names ("shift", "ctrl", "alt", "meta")
        """

    def normalize_event(self, qt_event: object) -> NormalizedEvent:
        """Normalize a Qt mouse event.

        Args:
            qt_event: A QMouseEvent

        Returns:
            A NormalizedEvent with platform-independent values
        """
        button = self.normalize_button(int(qt_event.button()))  # type: ignore
        modifiers = self.normalize_modifiers(int(qt_event.modifiers()))  # type: ignore

        button_id = BUTTON_ID_MAP.get(button, "unknown")

        return NormalizedEvent(
            button=button,
            button_id=button_id,
            modifiers=modifiers,
            x=qt_event.x(),  # type: ignore
            y=qt_event.y(),  # type: ignore
        )

    def button_to_id(self, button: CanonicalButton) -> str:
        """Convert a canonical button to string ID.

        Args:
            button: The canonical button

        Returns:
            The string ID (e.g., "left", "back")
        """
        return BUTTON_ID_MAP.get(button, "unknown")


class WindowsAdapter(PlatformAdapter):
    """Platform adapter for Windows."""

    # Qt button constants (from Qt.MouseButton)
    QT_LEFT = 1
    QT_RIGHT = 2
    QT_MIDDLE = 4
    QT_BACK = 8
    QT_FORWARD = 16
    QT_EXTRA1 = 32
    QT_EXTRA2 = 64

    # Qt modifier constants
    QT_SHIFT = 0x02000000
    QT_CTRL = 0x04000000
    QT_ALT = 0x08000000
    QT_META = 0x10000000

    def normalize_button(self, qt_button: int) -> CanonicalButton:
        """Normalize Qt button code on Windows."""
        mapping = {
            self.QT_LEFT: CanonicalButton.LEFT,
            self.QT_RIGHT: CanonicalButton.RIGHT,
            self.QT_MIDDLE: CanonicalButton.MIDDLE,
            self.QT_BACK: CanonicalButton.BACK,
            self.QT_FORWARD: CanonicalButton.FORWARD,
            self.QT_EXTRA1: CanonicalButton.EXTRA1,
            self.QT_EXTRA2: CanonicalButton.EXTRA2,
        }
        return mapping.get(qt_button, CanonicalButton.UNKNOWN)

    def normalize_modifiers(self, qt_modifiers: int) -> set[str]:
        """Normalize Qt modifiers on Windows."""
        result: set[str] = set()
        if qt_modifiers & self.QT_SHIFT:
            result.add("shift")
        if qt_modifiers & self.QT_CTRL:
            result.add("ctrl")
        if qt_modifiers & self.QT_ALT:
            result.add("alt")
        if qt_modifiers & self.QT_META:
            result.add("meta")
        return result


class MacOSAdapter(PlatformAdapter):
    """Platform adapter for macOS.

    On macOS, the Meta key is the Command key, and we may want to
    swap Ctrl/Meta for consistency with Windows/Linux conventions.
    """

    # Qt button constants (same values)
    QT_LEFT = 1
    QT_RIGHT = 2
    QT_MIDDLE = 4
    QT_BACK = 8
    QT_FORWARD = 16
    QT_EXTRA1 = 32
    QT_EXTRA2 = 64

    # Qt modifier constants
    QT_SHIFT = 0x02000000
    QT_CTRL = 0x04000000  # On macOS, this is Cmd
    QT_ALT = 0x08000000
    QT_META = 0x10000000  # On macOS, this is Ctrl

    def __init__(self, swap_ctrl_meta: bool = True) -> None:
        """Initialize the macOS adapter.

        Args:
            swap_ctrl_meta: If True, swap Ctrl and Meta to match
                           Windows/Linux conventions (Cmd acts as Ctrl)
        """
        self._swap_ctrl_meta = swap_ctrl_meta

    def normalize_button(self, qt_button: int) -> CanonicalButton:
        """Normalize Qt button code on macOS."""
        mapping = {
            self.QT_LEFT: CanonicalButton.LEFT,
            self.QT_RIGHT: CanonicalButton.RIGHT,
            self.QT_MIDDLE: CanonicalButton.MIDDLE,
            self.QT_BACK: CanonicalButton.BACK,
            self.QT_FORWARD: CanonicalButton.FORWARD,
            self.QT_EXTRA1: CanonicalButton.EXTRA1,
            self.QT_EXTRA2: CanonicalButton.EXTRA2,
        }
        return mapping.get(qt_button, CanonicalButton.UNKNOWN)

    def normalize_modifiers(self, qt_modifiers: int) -> set[str]:
        """Normalize Qt modifiers on macOS.

        By default, swaps Ctrl and Meta so Command key acts like
        Ctrl on other platforms.
        """
        result: set[str] = set()
        if qt_modifiers & self.QT_SHIFT:
            result.add("shift")
        if qt_modifiers & self.QT_ALT:
            result.add("alt")

        if self._swap_ctrl_meta:
            # Swap: Qt Ctrl (Cmd) -> canonical Ctrl
            #       Qt Meta (Ctrl) -> canonical Meta
            if qt_modifiers & self.QT_CTRL:
                result.add("ctrl")
            if qt_modifiers & self.QT_META:
                result.add("meta")
        else:
            if qt_modifiers & self.QT_CTRL:
                result.add("meta")  # Cmd -> Meta
            if qt_modifiers & self.QT_META:
                result.add("ctrl")  # Ctrl -> Ctrl

        return result


class LinuxAdapter(PlatformAdapter):
    """Platform adapter for Linux.

    Handles X11/Wayland differences if needed.
    """

    # Qt button constants
    QT_LEFT = 1
    QT_RIGHT = 2
    QT_MIDDLE = 4
    QT_BACK = 8
    QT_FORWARD = 16
    QT_EXTRA1 = 32
    QT_EXTRA2 = 64

    # Qt modifier constants
    QT_SHIFT = 0x02000000
    QT_CTRL = 0x04000000
    QT_ALT = 0x08000000
    QT_META = 0x10000000

    def normalize_button(self, qt_button: int) -> CanonicalButton:
        """Normalize Qt button code on Linux."""
        mapping = {
            self.QT_LEFT: CanonicalButton.LEFT,
            self.QT_RIGHT: CanonicalButton.RIGHT,
            self.QT_MIDDLE: CanonicalButton.MIDDLE,
            self.QT_BACK: CanonicalButton.BACK,
            self.QT_FORWARD: CanonicalButton.FORWARD,
            self.QT_EXTRA1: CanonicalButton.EXTRA1,
            self.QT_EXTRA2: CanonicalButton.EXTRA2,
        }
        return mapping.get(qt_button, CanonicalButton.UNKNOWN)

    def normalize_modifiers(self, qt_modifiers: int) -> set[str]:
        """Normalize Qt modifiers on Linux."""
        result: set[str] = set()
        if qt_modifiers & self.QT_SHIFT:
            result.add("shift")
        if qt_modifiers & self.QT_CTRL:
            result.add("ctrl")
        if qt_modifiers & self.QT_ALT:
            result.add("alt")
        if qt_modifiers & self.QT_META:
            result.add("meta")
        return result
