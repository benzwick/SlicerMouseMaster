"""Tests for ButtonDetector class."""

from __future__ import annotations

import pytest


class TestDetectedButton:
    """Tests for DetectedButton dataclass."""

    def test_default_values(self) -> None:
        """Test DetectedButton with default values."""
        from MouseMasterLib.button_detector import DetectedButton

        button = DetectedButton(qt_button=8)

        assert button.qt_button == 8
        assert button.suggested_id == ""
        assert button.suggested_name == ""
        assert button.press_count == 0


class TestDetectionSession:
    """Tests for DetectionSession dataclass."""

    def test_default_values(self) -> None:
        """Test DetectionSession with default values."""
        from MouseMasterLib.button_detector import DetectionSession

        session = DetectionSession()

        assert session.buttons == {}
        assert session.step == 0
        assert session.completed is False


class TestButtonDetector:
    """Tests for ButtonDetector class."""

    def test_start_detection(self) -> None:
        """Test starting a detection session."""
        from MouseMasterLib.button_detector import ButtonDetector

        detector = ButtonDetector()
        session = detector.start_detection(expected_buttons=5)

        assert session is not None
        assert session.total_steps == 5
        assert detector.is_detecting() is True

    def test_stop_detection(self) -> None:
        """Test stopping a detection session."""
        from MouseMasterLib.button_detector import ButtonDetector

        detector = ButtonDetector()
        detector.start_detection()

        session = detector.stop_detection()

        assert session is not None
        assert detector.is_detecting() is False

    def test_on_button_press_new_button(self) -> None:
        """Test detecting a new button."""
        from MouseMasterLib.button_detector import ButtonDetector

        detector = ButtonDetector()
        detector.start_detection()

        result = detector.on_button_press(8)

        assert result is True
        session = detector.get_session()
        assert 8 in session.buttons
        assert session.buttons[8].suggested_id == "left"  # First detected

    def test_on_button_press_duplicate(self) -> None:
        """Test pressing the same button twice."""
        from MouseMasterLib.button_detector import ButtonDetector

        detector = ButtonDetector()
        detector.start_detection()

        detector.on_button_press(8)
        detector.on_button_press(8)

        session = detector.get_session()
        assert session.buttons[8].press_count == 2

    def test_on_button_press_no_session(self) -> None:
        """Test button press without active session."""
        from MouseMasterLib.button_detector import ButtonDetector

        detector = ButtonDetector()

        result = detector.on_button_press(8)

        assert result is False

    def test_detection_order(self) -> None:
        """Test buttons are assigned IDs in detection order."""
        from MouseMasterLib.button_detector import ButtonDetector

        detector = ButtonDetector()
        detector.start_detection()

        detector.on_button_press(1)
        detector.on_button_press(2)
        detector.on_button_press(4)

        session = detector.get_session()
        assert session.buttons[1].suggested_id == "left"
        assert session.buttons[2].suggested_id == "right"
        assert session.buttons[4].suggested_id == "middle"

    def test_detection_complete_callback(self) -> None:
        """Test completion callback is called."""
        from MouseMasterLib.button_detector import ButtonDetector

        callback_received = []

        def on_complete(session):
            callback_received.append(session)

        detector = ButtonDetector()
        detector.start_detection(on_complete=on_complete, expected_buttons=2)

        detector.on_button_press(1)
        detector.on_button_press(2)

        assert len(callback_received) == 1
        assert callback_received[0].completed is True

    def test_button_callback(self) -> None:
        """Test button detection callback."""
        from MouseMasterLib.button_detector import ButtonDetector

        detected_buttons = []

        def on_button(detected):
            detected_buttons.append(detected)

        detector = ButtonDetector()
        detector.start_detection(on_button=on_button)

        detector.on_button_press(8)

        assert len(detected_buttons) == 1
        assert detected_buttons[0].qt_button == 8

    def test_generate_profile(self) -> None:
        """Test generating a mouse profile from detected buttons."""
        from MouseMasterLib.button_detector import ButtonDetector

        detector = ButtonDetector()
        detector.start_detection()

        detector.on_button_press(1)
        detector.on_button_press(2)
        detector.on_button_press(4)

        profile = detector.generate_profile(
            profile_id="my_mouse",
            profile_name="My Mouse",
            vendor="Custom",
        )

        assert profile["id"] == "my_mouse"
        assert profile["name"] == "My Mouse"
        assert profile["vendor"] == "Custom"
        assert len(profile["buttons"]) == 3

    def test_generate_profile_no_buttons(self) -> None:
        """Test generating profile without any detected buttons."""
        from MouseMasterLib.button_detector import ButtonDetector

        detector = ButtonDetector()
        detector.start_detection()

        with pytest.raises(ValueError, match="No buttons detected"):
            detector.generate_profile("id", "name")

    def test_generate_profile_no_session(self) -> None:
        """Test generating profile without session."""
        from MouseMasterLib.button_detector import ButtonDetector

        detector = ButtonDetector()

        with pytest.raises(ValueError, match="No buttons detected"):
            detector.generate_profile("id", "name")

    def test_finalize_detection(self) -> None:
        """Test manually finalizing detection."""
        from MouseMasterLib.button_detector import ButtonDetector

        detector = ButtonDetector()
        detector.start_detection(expected_buttons=10)

        detector.on_button_press(1)
        detector.on_button_press(2)

        session = detector.finalize_detection()

        assert session.completed is True

    def test_prompt_updates(self) -> None:
        """Test that prompts update during detection."""
        from MouseMasterLib.button_detector import ButtonDetector

        detector = ButtonDetector()
        session = detector.start_detection(expected_buttons=3)

        assert "button 1" in session.current_prompt.lower()

        detector.on_button_press(1)
        assert "button 2" in session.current_prompt.lower()

        detector.on_button_press(2)
        assert "button 3" in session.current_prompt.lower()

        detector.on_button_press(4)
        assert "complete" in session.current_prompt.lower()
