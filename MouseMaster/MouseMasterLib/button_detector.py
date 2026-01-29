"""Button detection for unknown mice.

This module provides interactive button detection to help users
configure mice that don't have built-in profiles.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable, ClassVar

logger = logging.getLogger(__name__)


@dataclass
class DetectedButton:
    """A detected mouse button.

    Attributes:
        qt_button: The Qt button code
        suggested_id: Suggested canonical ID
        suggested_name: Suggested display name
        press_count: Number of times detected
    """

    qt_button: int
    suggested_id: str = ""
    suggested_name: str = ""
    press_count: int = 0


@dataclass
class DetectionSession:
    """State for a button detection session.

    Attributes:
        buttons: Detected buttons (qt_button -> DetectedButton)
        current_prompt: Current instruction for user
        step: Current step number
        total_steps: Total expected steps
        completed: Whether detection is complete
    """

    buttons: dict[int, DetectedButton] = field(default_factory=dict)
    current_prompt: str = "Press any mouse button..."
    step: int = 0
    total_steps: int = 0
    completed: bool = False


class ButtonDetector:
    """Interactive button detection for creating mouse profiles.

    The ButtonDetector guides users through pressing each button on
    their mouse to capture the Qt button codes, which can then be
    used to create a custom mouse profile.

    Usage:
        detector = ButtonDetector()
        detector.start_detection(on_button=handle_button, on_complete=handle_complete)
        # ... Qt events call detector.on_button_press(qt_button) ...
        profile = detector.generate_profile("my_mouse", "My Mouse")
    """

    # Standard button suggestions based on order detected
    SUGGESTED_BUTTONS: ClassVar[list[tuple[str, str]]] = [
        ("left", "Left Click"),
        ("right", "Right Click"),
        ("middle", "Middle Click"),
        ("back", "Back"),
        ("forward", "Forward"),
        ("thumb", "Thumb Button"),
        ("extra1", "Extra Button 1"),
        ("extra2", "Extra Button 2"),
    ]

    def __init__(self) -> None:
        """Initialize the detector."""
        self._session: DetectionSession | None = None
        self._on_button: Callable[[DetectedButton], None] | None = None
        self._on_complete: Callable[[DetectionSession], None] | None = None
        self._detection_order: list[int] = []

    def start_detection(
        self,
        on_button: Callable[[DetectedButton], None] | None = None,
        on_complete: Callable[[DetectionSession], None] | None = None,
        expected_buttons: int = 5,
    ) -> DetectionSession:
        """Start a new button detection session.

        Args:
            on_button: Callback when a button is detected
            on_complete: Callback when detection is complete
            expected_buttons: Expected number of buttons to detect

        Returns:
            The new DetectionSession
        """
        self._session = DetectionSession(
            total_steps=expected_buttons,
            current_prompt="Press button 1 (usually Left Click)...",
        )
        self._on_button = on_button
        self._on_complete = on_complete
        self._detection_order = []

        logger.info(f"Started button detection session, expecting {expected_buttons} buttons")
        return self._session

    def stop_detection(self) -> DetectionSession | None:
        """Stop the current detection session.

        Returns:
            The session state, or None if no session active
        """
        session = self._session
        self._session = None
        self._on_button = None
        self._on_complete = None
        self._detection_order = []

        if session:
            logger.info(f"Detection stopped with {len(session.buttons)} buttons")
        return session

    def on_button_press(self, qt_button: int) -> bool:
        """Handle a button press during detection.

        Args:
            qt_button: The Qt button code

        Returns:
            True if the press was handled, False if no session active
        """
        if not self._session:
            return False

        # Check if already detected
        if qt_button in self._session.buttons:
            self._session.buttons[qt_button].press_count += 1
            logger.debug(
                f"Button {qt_button} pressed again (count: {self._session.buttons[qt_button].press_count})"
            )
            return True

        # New button detected
        step = len(self._session.buttons)
        suggested = (
            self.SUGGESTED_BUTTONS[step]
            if step < len(self.SUGGESTED_BUTTONS)
            else (f"button{step}", f"Button {step}")
        )

        detected = DetectedButton(
            qt_button=qt_button,
            suggested_id=suggested[0],
            suggested_name=suggested[1],
            press_count=1,
        )

        self._session.buttons[qt_button] = detected
        self._detection_order.append(qt_button)
        self._session.step = step + 1

        # Update prompt
        if self._session.step < self._session.total_steps:
            next_name = (
                self.SUGGESTED_BUTTONS[self._session.step][1]
                if self._session.step < len(self.SUGGESTED_BUTTONS)
                else f"Button {self._session.step + 1}"
            )
            self._session.current_prompt = f"Press button {self._session.step + 1} ({next_name})..."
        else:
            self._session.current_prompt = "Detection complete!"
            self._session.completed = True

        logger.info(f"Detected button {qt_button} as {detected.suggested_name}")

        # Callbacks
        if self._on_button:
            self._on_button(detected)

        if self._session.completed and self._on_complete:
            self._on_complete(self._session)

        return True

    def get_session(self) -> DetectionSession | None:
        """Get the current detection session.

        Returns:
            The current session, or None if not detecting
        """
        return self._session

    def is_detecting(self) -> bool:
        """Check if a detection session is active.

        Returns:
            True if detecting
        """
        return self._session is not None and not self._session.completed

    def generate_profile(
        self,
        profile_id: str,
        profile_name: str,
        vendor: str = "Custom",
    ) -> dict:
        """Generate a mouse profile from the detected buttons.

        Args:
            profile_id: Unique ID for the profile
            profile_name: Display name for the profile
            vendor: Vendor name

        Returns:
            A dictionary suitable for MouseProfile.from_dict()

        Raises:
            ValueError: If no buttons have been detected
        """
        if not self._session or not self._session.buttons:
            raise ValueError("No buttons detected")

        # Build buttons list in detection order
        buttons = []
        for qt_button in self._detection_order:
            detected = self._session.buttons[qt_button]
            button_data = {
                "id": detected.suggested_id,
                "name": detected.suggested_name,
                "qtButton": qt_button,
                "remappable": detected.suggested_id not in ("left", "right"),
            }
            buttons.append(button_data)

        profile = {
            "id": profile_id,
            "name": profile_name,
            "vendor": vendor,
            "vendorId": "0x0000",
            "productIds": [],
            "buttons": buttons,
            "features": {},
        }

        logger.info(f"Generated profile '{profile_name}' with {len(buttons)} buttons")
        return profile

    def finalize_detection(self) -> DetectionSession | None:
        """Mark detection as complete and return results.

        Call this when user indicates they're done pressing buttons.

        Returns:
            The completed session, or None if not detecting
        """
        if not self._session:
            return None

        self._session.completed = True
        self._session.current_prompt = "Detection complete!"

        if self._on_complete:
            self._on_complete(self._session)

        return self._session
