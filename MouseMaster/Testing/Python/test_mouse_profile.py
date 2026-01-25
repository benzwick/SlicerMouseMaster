"""Tests for MouseProfile and related classes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


class TestMouseButton:
    """Tests for MouseButton dataclass."""

    def test_from_dict_basic(self) -> None:
        """Test creating MouseButton from basic dictionary."""
        from MouseMasterLib.mouse_profile import MouseButton

        data = {
            "id": "back",
            "name": "Back Button",
            "qtButton": 8,
        }
        button = MouseButton.from_dict(data)

        assert button.id == "back"
        assert button.name == "Back Button"
        assert button.qt_button == 8
        assert button.remappable is True  # default
        assert button.default_action is None

    def test_from_dict_full(self) -> None:
        """Test creating MouseButton with all fields."""
        from MouseMasterLib.mouse_profile import MouseButton

        data = {
            "id": "thumb",
            "name": "Thumb Button",
            "qtButton": 32,
            "remappable": True,
            "defaultAction": "view_toggle_crosshair",
        }
        button = MouseButton.from_dict(data)

        assert button.id == "thumb"
        assert button.qt_button == 32
        assert button.remappable is True
        assert button.default_action == "view_toggle_crosshair"

    def test_to_dict(self) -> None:
        """Test serializing MouseButton to dictionary."""
        from MouseMasterLib.mouse_profile import MouseButton

        button = MouseButton(
            id="forward",
            name="Forward Button",
            qt_button=16,
            remappable=True,
            default_action="edit_redo",
        )
        data = button.to_dict()

        assert data["id"] == "forward"
        assert data["name"] == "Forward Button"
        assert data["qtButton"] == 16
        assert data["remappable"] is True
        assert data["defaultAction"] == "edit_redo"

    def test_to_dict_no_default_action(self) -> None:
        """Test serializing MouseButton without default action."""
        from MouseMasterLib.mouse_profile import MouseButton

        button = MouseButton(id="middle", name="Middle", qt_button=4)
        data = button.to_dict()

        assert "defaultAction" not in data


class TestMouseFeatures:
    """Tests for MouseFeatures dataclass."""

    def test_from_dict_empty(self) -> None:
        """Test creating MouseFeatures from empty dict."""
        from MouseMasterLib.mouse_profile import MouseFeatures

        features = MouseFeatures.from_dict({})

        assert features.horizontal_scroll is False
        assert features.thumb_wheel is False
        assert features.gesture_button is False

    def test_from_dict_full(self) -> None:
        """Test creating MouseFeatures with all fields."""
        from MouseMasterLib.mouse_profile import MouseFeatures

        data = {
            "horizontalScroll": True,
            "thumbWheel": True,
            "gestureButton": False,
        }
        features = MouseFeatures.from_dict(data)

        assert features.horizontal_scroll is True
        assert features.thumb_wheel is True
        assert features.gesture_button is False

    def test_to_dict(self) -> None:
        """Test serializing MouseFeatures."""
        from MouseMasterLib.mouse_profile import MouseFeatures

        features = MouseFeatures(
            horizontal_scroll=True,
            thumb_wheel=False,
            gesture_button=True,
        )
        data = features.to_dict()

        assert data["horizontalScroll"] is True
        assert data["thumbWheel"] is False
        assert data["gestureButton"] is True


class TestMouseProfile:
    """Tests for MouseProfile dataclass."""

    def test_from_dict(self, sample_mouse_profile_data: dict[str, Any]) -> None:
        """Test creating MouseProfile from dictionary."""
        from MouseMasterLib.mouse_profile import MouseProfile

        profile = MouseProfile.from_dict(sample_mouse_profile_data)

        assert profile.id == "test_mouse"
        assert profile.name == "Test Mouse"
        assert profile.vendor == "Test Vendor"
        assert profile.vendor_id == "0x1234"
        assert profile.product_ids == ["0x5678"]
        assert len(profile.buttons) == 4
        assert profile.features.horizontal_scroll is True

    def test_from_json_file(self, temp_json_file: Path) -> None:
        """Test loading MouseProfile from JSON file."""
        from MouseMasterLib.mouse_profile import MouseProfile

        profile = MouseProfile.from_json_file(temp_json_file)

        assert profile.id == "test_mouse"
        assert len(profile.buttons) == 4

    def test_to_dict(self, sample_mouse_profile_data: dict[str, Any]) -> None:
        """Test serializing MouseProfile."""
        from MouseMasterLib.mouse_profile import MouseProfile

        profile = MouseProfile.from_dict(sample_mouse_profile_data)
        data = profile.to_dict()

        assert data["id"] == "test_mouse"
        assert len(data["buttons"]) == 4
        assert "features" in data

    def test_to_json_file(self, tmp_path: Path, sample_mouse_profile_data: dict) -> None:
        """Test saving MouseProfile to JSON file."""
        from MouseMasterLib.mouse_profile import MouseProfile

        profile = MouseProfile.from_dict(sample_mouse_profile_data)
        output_path = tmp_path / "output.json"
        profile.to_json_file(output_path)

        assert output_path.exists()
        with open(output_path) as f:
            loaded = json.load(f)
        assert loaded["id"] == "test_mouse"

    def test_get_button(self, sample_mouse_profile_data: dict) -> None:
        """Test getting button by ID."""
        from MouseMasterLib.mouse_profile import MouseProfile

        profile = MouseProfile.from_dict(sample_mouse_profile_data)

        back_button = profile.get_button("back")
        assert back_button is not None
        assert back_button.qt_button == 8

        missing = profile.get_button("nonexistent")
        assert missing is None

    def test_get_button_by_qt_code(self, sample_mouse_profile_data: dict) -> None:
        """Test getting button by Qt code."""
        from MouseMasterLib.mouse_profile import MouseProfile

        profile = MouseProfile.from_dict(sample_mouse_profile_data)

        button = profile.get_button_by_qt_code(8)
        assert button is not None
        assert button.id == "back"

        missing = profile.get_button_by_qt_code(999)
        assert missing is None

    def test_get_remappable_buttons(self, sample_mouse_profile_data: dict) -> None:
        """Test getting remappable buttons."""
        from MouseMasterLib.mouse_profile import MouseProfile

        profile = MouseProfile.from_dict(sample_mouse_profile_data)
        remappable = profile.get_remappable_buttons()

        assert len(remappable) == 2  # middle and back
        assert all(b.remappable for b in remappable)

    def test_button_count(self, sample_mouse_profile_data: dict) -> None:
        """Test button count properties."""
        from MouseMasterLib.mouse_profile import MouseProfile

        profile = MouseProfile.from_dict(sample_mouse_profile_data)

        assert profile.button_count == 4
        assert profile.remappable_count == 2

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Test loading from nonexistent file."""
        from MouseMasterLib.mouse_profile import MouseProfile

        with pytest.raises(FileNotFoundError):
            MouseProfile.from_json_file(tmp_path / "nonexistent.json")

    def test_invalid_json(self, tmp_path: Path) -> None:
        """Test loading invalid JSON."""
        from MouseMasterLib.mouse_profile import MouseProfile

        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not valid json")

        with pytest.raises(json.JSONDecodeError):
            MouseProfile.from_json_file(bad_file)
