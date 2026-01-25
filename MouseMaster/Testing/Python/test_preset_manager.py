"""Tests for PresetManager and related classes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


class TestMapping:
    """Tests for Mapping dataclass."""

    def test_from_dict_basic(self) -> None:
        """Test creating Mapping from basic dictionary."""
        from MouseMasterLib.preset_manager import Mapping

        data = {"action": "edit_undo"}
        mapping = Mapping.from_dict(data)

        assert mapping.action == "edit_undo"
        assert mapping.action_id is None
        assert mapping.parameters == {}

    def test_from_dict_full(self) -> None:
        """Test creating Mapping with all fields."""
        from MouseMasterLib.preset_manager import Mapping

        data = {
            "action": "python_command",
            "actionId": "custom_cmd",
            "parameters": {"command": "print('hello')"},
        }
        mapping = Mapping.from_dict(data)

        assert mapping.action == "python_command"
        assert mapping.action_id == "custom_cmd"
        assert mapping.parameters["command"] == "print('hello')"

    def test_to_dict(self) -> None:
        """Test serializing Mapping."""
        from MouseMasterLib.preset_manager import Mapping

        mapping = Mapping(
            action="slicer_action",
            action_id="EditUndoAction",
            parameters={"key": "value"},
        )
        data = mapping.to_dict()

        assert data["action"] == "slicer_action"
        assert data["actionId"] == "EditUndoAction"
        assert data["parameters"]["key"] == "value"

    def test_to_dict_minimal(self) -> None:
        """Test serializing Mapping with minimal data."""
        from MouseMasterLib.preset_manager import Mapping

        mapping = Mapping(action="edit_undo")
        data = mapping.to_dict()

        assert data == {"action": "edit_undo"}
        assert "actionId" not in data
        assert "parameters" not in data


class TestPreset:
    """Tests for Preset dataclass."""

    def test_from_dict(self, sample_preset_data: dict[str, Any]) -> None:
        """Test creating Preset from dictionary."""
        from MouseMasterLib.preset_manager import Preset

        preset = Preset.from_dict(sample_preset_data)

        assert preset.id == "test_preset"
        assert preset.name == "Test Preset"
        assert preset.version == "1.0"
        assert preset.mouse_id == "test_mouse"
        assert preset.author == "Test Author"
        assert "middle" in preset.mappings
        assert "SegmentEditor" in preset.context_mappings

    def test_from_json_file(self, temp_preset_file: Path) -> None:
        """Test loading Preset from JSON file."""
        from MouseMasterLib.preset_manager import Preset

        preset = Preset.from_json_file(temp_preset_file)

        assert preset.id == "test_preset"
        assert len(preset.mappings) == 2

    def test_to_dict(self, sample_preset_data: dict) -> None:
        """Test serializing Preset."""
        from MouseMasterLib.preset_manager import Preset

        preset = Preset.from_dict(sample_preset_data)
        data = preset.to_dict()

        assert data["id"] == "test_preset"
        assert "mappings" in data
        assert "contextMappings" in data

    def test_to_json_file(self, tmp_path: Path, sample_preset_data: dict) -> None:
        """Test saving Preset to JSON file."""
        from MouseMasterLib.preset_manager import Preset

        preset = Preset.from_dict(sample_preset_data)
        output_path = tmp_path / "output.json"
        preset.to_json_file(output_path)

        assert output_path.exists()
        with open(output_path) as f:
            loaded = json.load(f)
        assert loaded["id"] == "test_preset"

    def test_get_mapping_default(self, sample_preset_data: dict) -> None:
        """Test getting default mapping."""
        from MouseMasterLib.preset_manager import Preset

        preset = Preset.from_dict(sample_preset_data)

        mapping = preset.get_mapping("middle")
        assert mapping is not None
        assert mapping.action == "view_reset_3d"

    def test_get_mapping_with_context(self, sample_preset_data: dict) -> None:
        """Test getting context-specific mapping."""
        from MouseMasterLib.preset_manager import Preset

        preset = Preset.from_dict(sample_preset_data)

        # Context-specific should override
        mapping = preset.get_mapping("back", context="SegmentEditor")
        assert mapping is not None
        assert mapping.action == "segment_previous"

        # Default when no context override
        mapping = preset.get_mapping("middle", context="SegmentEditor")
        assert mapping is not None
        assert mapping.action == "view_reset_3d"

    def test_get_mapping_not_found(self, sample_preset_data: dict) -> None:
        """Test getting nonexistent mapping."""
        from MouseMasterLib.preset_manager import Preset

        preset = Preset.from_dict(sample_preset_data)

        mapping = preset.get_mapping("nonexistent")
        assert mapping is None

    def test_set_mapping(self, sample_preset_data: dict) -> None:
        """Test setting a mapping."""
        from MouseMasterLib.preset_manager import Mapping, Preset

        preset = Preset.from_dict(sample_preset_data)

        new_mapping = Mapping(action="new_action")
        preset.set_mapping("forward", new_mapping)

        retrieved = preset.get_mapping("forward")
        assert retrieved is not None
        assert retrieved.action == "new_action"

    def test_set_mapping_with_context(self, sample_preset_data: dict) -> None:
        """Test setting a context-specific mapping."""
        from MouseMasterLib.preset_manager import Mapping, Preset

        preset = Preset.from_dict(sample_preset_data)

        new_mapping = Mapping(action="custom_action")
        preset.set_mapping("middle", new_mapping, context="Markups")

        retrieved = preset.get_mapping("middle", context="Markups")
        assert retrieved is not None
        assert retrieved.action == "custom_action"

    def test_remove_mapping(self, sample_preset_data: dict) -> None:
        """Test removing a mapping."""
        from MouseMasterLib.preset_manager import Preset

        preset = Preset.from_dict(sample_preset_data)

        assert preset.remove_mapping("middle") is True
        assert preset.get_mapping("middle") is None

        # Removing again returns False
        assert preset.remove_mapping("middle") is False

    def test_remove_context_mapping(self, sample_preset_data: dict) -> None:
        """Test removing a context-specific mapping."""
        from MouseMasterLib.preset_manager import Preset

        preset = Preset.from_dict(sample_preset_data)

        result = preset.remove_mapping("back", context="SegmentEditor")
        assert result is True

        # Now falls back to default
        mapping = preset.get_mapping("back", context="SegmentEditor")
        assert mapping.action == "edit_undo"


class TestPresetManager:
    """Tests for PresetManager class."""

    def test_init(self, tmp_path: Path) -> None:
        """Test PresetManager initialization."""
        from MouseMasterLib.preset_manager import PresetManager

        manager = PresetManager(
            builtin_dir=tmp_path / "builtin",
            user_dir=tmp_path / "user",
        )

        assert manager._builtin_dir is not None
        assert manager._user_dir is not None

    def test_load_all_empty_dirs(self, tmp_path: Path) -> None:
        """Test loading from empty/nonexistent directories."""
        from MouseMasterLib.preset_manager import PresetManager

        manager = PresetManager(
            builtin_dir=tmp_path / "nonexistent",
            user_dir=tmp_path / "also_nonexistent",
        )
        manager.load_all()

        assert len(manager.get_all_presets()) == 0

    def test_load_from_directory(
        self, tmp_path: Path, sample_preset_data: dict
    ) -> None:
        """Test loading presets from directory."""
        from MouseMasterLib.preset_manager import PresetManager

        # Create preset file
        preset_dir = tmp_path / "presets"
        preset_dir.mkdir()
        preset_file = preset_dir / "test.json"
        with open(preset_file, "w") as f:
            json.dump(sample_preset_data, f)

        manager = PresetManager(builtin_dir=preset_dir)
        manager.load_all()

        presets = manager.get_all_presets()
        assert len(presets) == 1
        assert presets[0].id == "test_preset"

    def test_get_preset(self, tmp_path: Path, sample_preset_data: dict) -> None:
        """Test getting preset by ID."""
        from MouseMasterLib.preset_manager import PresetManager

        preset_dir = tmp_path / "presets"
        preset_dir.mkdir()
        with open(preset_dir / "test.json", "w") as f:
            json.dump(sample_preset_data, f)

        manager = PresetManager(builtin_dir=preset_dir)
        manager.load_all()

        preset = manager.get_preset("test_preset")
        assert preset is not None
        assert preset.name == "Test Preset"

        assert manager.get_preset("nonexistent") is None

    def test_get_presets_for_mouse(
        self, tmp_path: Path, sample_preset_data: dict
    ) -> None:
        """Test getting presets for a specific mouse."""
        from MouseMasterLib.preset_manager import PresetManager

        preset_dir = tmp_path / "presets"
        preset_dir.mkdir()

        # Create two presets for different mice
        with open(preset_dir / "test1.json", "w") as f:
            json.dump(sample_preset_data, f)

        other_preset = sample_preset_data.copy()
        other_preset["id"] = "other_preset"
        other_preset["mouseId"] = "other_mouse"
        with open(preset_dir / "test2.json", "w") as f:
            json.dump(other_preset, f)

        manager = PresetManager(builtin_dir=preset_dir)
        manager.load_all()

        presets = manager.get_presets_for_mouse("test_mouse")
        assert len(presets) == 1
        assert presets[0].id == "test_preset"

    def test_save_preset(self, tmp_path: Path, sample_preset_data: dict) -> None:
        """Test saving a preset."""
        from MouseMasterLib.preset_manager import Preset, PresetManager

        user_dir = tmp_path / "user"
        manager = PresetManager(user_dir=user_dir)

        preset = Preset.from_dict(sample_preset_data)
        manager.save_preset(preset)

        saved_file = user_dir / "test_preset.json"
        assert saved_file.exists()

    def test_save_preset_no_user_dir(self, sample_preset_data: dict) -> None:
        """Test saving without user directory configured."""
        from MouseMasterLib.preset_manager import Preset, PresetManager

        manager = PresetManager()
        preset = Preset.from_dict(sample_preset_data)

        with pytest.raises(ValueError, match="not configured"):
            manager.save_preset(preset)

    def test_delete_preset(self, tmp_path: Path, sample_preset_data: dict) -> None:
        """Test deleting a preset."""
        from MouseMasterLib.preset_manager import Preset, PresetManager

        user_dir = tmp_path / "user"
        manager = PresetManager(user_dir=user_dir)

        preset = Preset.from_dict(sample_preset_data)
        manager.save_preset(preset)

        assert manager.delete_preset("test_preset") is True
        assert not (user_dir / "test_preset.json").exists()
        assert manager.delete_preset("test_preset") is False

    def test_export_import_preset(
        self, tmp_path: Path, sample_preset_data: dict
    ) -> None:
        """Test exporting and importing a preset."""
        from MouseMasterLib.preset_manager import Preset, PresetManager

        user_dir = tmp_path / "user"
        manager = PresetManager(user_dir=user_dir)

        # Save preset first
        preset = Preset.from_dict(sample_preset_data)
        manager.save_preset(preset)

        # Export
        export_path = tmp_path / "exported.json"
        manager.export_preset("test_preset", export_path)
        assert export_path.exists()

        # Import into new manager
        new_manager = PresetManager(user_dir=tmp_path / "new_user")
        imported = new_manager.import_preset(export_path)
        assert imported.id == "test_preset"
