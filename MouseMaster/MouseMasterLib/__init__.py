"""MouseMasterLib - Core library for SlicerMouseMaster extension.

This package provides mouse customization functionality for 3D Slicer:
- EventHandler: Qt event filter for intercepting mouse buttons
- MouseProfile: Mouse definition dataclass
- PresetManager: Load/save/export button mapping presets
- ActionRegistry: Registry of available Slicer actions
- PlatformAdapter: Cross-platform button normalization
- ButtonDetector: Interactive button code detection
"""

from MouseMasterLib.action_registry import ActionRegistry
from MouseMasterLib.button_detector import ButtonDetector
from MouseMasterLib.event_handler import MouseMasterEventHandler
from MouseMasterLib.mouse_profile import MouseButton, MouseProfile
from MouseMasterLib.platform_adapter import PlatformAdapter
from MouseMasterLib.preset_manager import Mapping, Preset, PresetManager

__all__ = [
    "ActionRegistry",
    "ButtonDetector",
    "Mapping",
    "MouseButton",
    "MouseMasterEventHandler",
    "MouseProfile",
    "PlatformAdapter",
    "Preset",
    "PresetManager",
]

__version__ = "0.1.0"
