"""Preset management for button mappings.

This module provides classes for loading, saving, and managing button
mapping presets.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

# Current preset format version
CURRENT_PRESET_VERSION = "1.0"

# Migration functions: version -> function that transforms data dict
# Each migration takes data dict and returns migrated data dict
PRESET_MIGRATIONS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    # Example migration from 0.9 to 1.0:
    # "0.9": lambda data: {**data, "newField": "defaultValue"},
}


def migrate_preset_data(data: dict[str, Any]) -> dict[str, Any]:
    """Migrate preset data from old versions to current version.

    Args:
        data: Raw preset data dictionary

    Returns:
        Migrated data dictionary at current version
    """
    version = data.get("version", "1.0")

    # Already at current version
    if version == CURRENT_PRESET_VERSION:
        return data

    # Apply migrations in order
    # This is a simple linear migration; for complex version graphs,
    # a more sophisticated approach would be needed
    migrated = data.copy()
    if version in PRESET_MIGRATIONS:
        migrated = PRESET_MIGRATIONS[version](migrated)
        migrated["version"] = CURRENT_PRESET_VERSION
        logger.info(f"Migrated preset from version {version} to {CURRENT_PRESET_VERSION}")

    return migrated


@dataclass
class Mapping:
    """A single button-to-action mapping.

    Attributes:
        action: The action type (e.g., "slicer_action", "python_command")
        action_id: Specific action identifier
        parameters: Optional parameters for the action
    """

    action: str
    action_id: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Mapping:
        """Create a Mapping from a dictionary."""
        return cls(
            action=data["action"],
            action_id=data.get("actionId"),
            parameters=data.get("parameters", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result: dict[str, Any] = {"action": self.action}
        if self.action_id:
            result["actionId"] = self.action_id
        if self.parameters:
            result["parameters"] = self.parameters
        return result


@dataclass
class Preset:
    """A complete button mapping preset.

    Presets define how mouse buttons are mapped to actions, optionally
    with context-sensitive overrides for specific Slicer modules.

    Attributes:
        id: Unique identifier for the preset
        name: Human-readable name
        version: Preset format version
        mouse_id: ID of the mouse profile this preset is for
        mappings: Default button mappings (button_id -> Mapping)
        context_mappings: Per-module overrides (module -> button_id -> Mapping)
        author: Optional author name
        description: Optional description
    """

    id: str
    name: str
    version: str
    mouse_id: str
    mappings: dict[str, Mapping] = field(default_factory=dict)
    context_mappings: dict[str, dict[str, Mapping]] = field(default_factory=dict)
    author: str | None = None
    description: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Preset:
        """Create a Preset from a dictionary."""
        # Migrate old versions to current version
        data = migrate_preset_data(data)

        # Parse default mappings
        mappings: dict[str, Mapping] = {}
        for button_id, mapping_data in data.get("mappings", {}).items():
            mappings[button_id] = Mapping.from_dict(mapping_data)

        # Parse context-specific mappings
        context_mappings: dict[str, dict[str, Mapping]] = {}
        for context, context_data in data.get("contextMappings", {}).items():
            context_mappings[context] = {}
            for button_id, mapping_data in context_data.items():
                context_mappings[context][button_id] = Mapping.from_dict(mapping_data)

        return cls(
            id=data["id"],
            name=data["name"],
            version=data.get("version", "1.0"),
            mouse_id=data["mouseId"],
            mappings=mappings,
            context_mappings=context_mappings,
            author=data.get("author"),
            description=data.get("description"),
        )

    @classmethod
    def from_json_file(cls, path: Path | str) -> Preset:
        """Load a Preset from a JSON file.

        Args:
            path: Path to the JSON file

        Returns:
            Loaded Preset

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is invalid
            KeyError: If required fields are missing
        """
        path = Path(path)
        logger.debug(f"Loading preset from {path}")

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "mouseId": self.mouse_id,
            "mappings": {k: v.to_dict() for k, v in self.mappings.items()},
        }

        if self.context_mappings:
            result["contextMappings"] = {
                context: {k: v.to_dict() for k, v in mappings.items()}
                for context, mappings in self.context_mappings.items()
            }

        if self.author:
            result["author"] = self.author
        if self.description:
            result["description"] = self.description

        return result

    def to_json_file(self, path: Path | str) -> None:
        """Save the preset to a JSON file.

        Args:
            path: Path to save the JSON file
        """
        path = Path(path)
        logger.debug(f"Saving preset to {path}")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    def get_mapping(self, button_id: str, context: str | None = None) -> Mapping | None:
        """Get the mapping for a button, considering context.

        Looks up context-specific mapping first, falls back to default.

        Args:
            button_id: The button ID to look up
            context: Optional context (Slicer module name)

        Returns:
            The Mapping if found, None otherwise
        """
        # Try context-specific first
        if (
            context
            and context in self.context_mappings
            and button_id in self.context_mappings[context]
        ):
            return self.context_mappings[context][button_id]

        # Fall back to default
        return self.mappings.get(button_id)

    def set_mapping(self, button_id: str, mapping: Mapping, context: str | None = None) -> None:
        """Set a mapping for a button.

        Args:
            button_id: The button ID
            mapping: The mapping to set
            context: Optional context for context-specific mapping
        """
        if context:
            if context not in self.context_mappings:
                self.context_mappings[context] = {}
            self.context_mappings[context][button_id] = mapping
        else:
            self.mappings[button_id] = mapping

    def remove_mapping(self, button_id: str, context: str | None = None) -> bool:
        """Remove a mapping for a button.

        Args:
            button_id: The button ID
            context: Optional context for context-specific mapping

        Returns:
            True if mapping was removed, False if not found
        """
        if (
            context
            and context in self.context_mappings
            and button_id in self.context_mappings[context]
        ):
            del self.context_mappings[context][button_id]
            return True
        if not context and button_id in self.mappings:
            del self.mappings[button_id]
            return True
        return False


class PresetManager:
    """Manages loading, saving, and organizing presets.

    The PresetManager handles:
    - Loading built-in presets from extension resources
    - Loading user presets from user directory
    - Saving new/modified presets
    - Exporting/importing presets for sharing
    """

    def __init__(
        self,
        builtin_dir: Path | str | None = None,
        user_dir: Path | str | None = None,
    ) -> None:
        """Initialize the PresetManager.

        Args:
            builtin_dir: Directory containing built-in presets
            user_dir: Directory for user presets
        """
        self._builtin_dir = Path(builtin_dir) if builtin_dir else None
        self._user_dir = Path(user_dir) if user_dir else None
        self._presets: dict[str, Preset] = {}
        self._loaded = False

    def load_all(self) -> None:
        """Load all presets from builtin and user directories."""
        self._presets.clear()

        # Load built-in presets first
        if self._builtin_dir and self._builtin_dir.exists():
            self._load_from_directory(self._builtin_dir, is_builtin=True)

        # Load user presets (can override built-in)
        if self._user_dir and self._user_dir.exists():
            self._load_from_directory(self._user_dir, is_builtin=False)

        self._loaded = True
        logger.info(f"Loaded {len(self._presets)} presets")

    def _load_from_directory(self, directory: Path, is_builtin: bool) -> None:
        """Load all preset files from a directory.

        Args:
            directory: Directory to load from
            is_builtin: Whether these are built-in presets
        """
        for path in directory.glob("*.json"):
            try:
                preset = Preset.from_json_file(path)
                self._presets[preset.id] = preset
                logger.debug(f"Loaded preset: {preset.id} ({'builtin' if is_builtin else 'user'})")
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to load preset {path}: {e}")

    def get_preset(self, preset_id: str) -> Preset | None:
        """Get a preset by ID.

        Args:
            preset_id: The preset ID

        Returns:
            The Preset if found, None otherwise
        """
        if not self._loaded:
            self.load_all()
        return self._presets.get(preset_id)

    def get_presets_for_mouse(self, mouse_id: str) -> list[Preset]:
        """Get all presets for a specific mouse.

        Args:
            mouse_id: The mouse profile ID

        Returns:
            List of presets for this mouse
        """
        if not self._loaded:
            self.load_all()
        return [p for p in self._presets.values() if p.mouse_id == mouse_id]

    def get_all_presets(self) -> list[Preset]:
        """Get all loaded presets.

        Returns:
            List of all presets
        """
        if not self._loaded:
            self.load_all()
        return list(self._presets.values())

    def save_preset(self, preset: Preset) -> None:
        """Save a preset to the user directory.

        Args:
            preset: The preset to save

        Raises:
            ValueError: If user directory is not configured
        """
        if not self._user_dir:
            raise ValueError("User preset directory not configured")

        self._user_dir.mkdir(parents=True, exist_ok=True)
        path = self._user_dir / f"{preset.id}.json"
        preset.to_json_file(path)
        self._presets[preset.id] = preset
        logger.info(f"Saved preset: {preset.id}")

    def delete_preset(self, preset_id: str) -> bool:
        """Delete a user preset.

        Args:
            preset_id: The preset ID to delete

        Returns:
            True if deleted, False if not found or is built-in
        """
        if not self._user_dir:
            return False

        path = self._user_dir / f"{preset_id}.json"
        if path.exists():
            path.unlink()
            if preset_id in self._presets:
                del self._presets[preset_id]
            logger.info(f"Deleted preset: {preset_id}")
            return True
        return False

    def export_preset(self, preset_id: str, path: Path | str) -> None:
        """Export a preset to a file for sharing.

        Args:
            preset_id: The preset ID to export
            path: Destination path

        Raises:
            KeyError: If preset not found
        """
        preset = self.get_preset(preset_id)
        if not preset:
            raise KeyError(f"Preset not found: {preset_id}")
        preset.to_json_file(path)
        logger.info(f"Exported preset {preset_id} to {path}")

    def import_preset(self, path: Path | str) -> Preset:
        """Import a preset from a file.

        Args:
            path: Path to the preset file

        Returns:
            The imported Preset

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is invalid
        """
        preset = Preset.from_json_file(path)

        # Save to user directory
        if self._user_dir:
            self.save_preset(preset)

        logger.info(f"Imported preset: {preset.id}")
        return preset
