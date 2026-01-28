"""pytest configuration and fixtures for MouseMaster tests.

These tests are designed to run outside of Slicer with pytest.
They test the pure-Python components that don't require Qt/VTK/Slicer.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

# Add the module to the path for imports
MODULE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(MODULE_DIR))

# ============================================================================
# Centralized Slicer/Qt/VTK mock setup
# ============================================================================
# These mocks must be installed in sys.modules BEFORE any MouseMasterLib
# imports occur. This is done at module load time.

_MOCK_SLICER = MagicMock(name="slicer")
_MOCK_SLICER_UTIL = MagicMock(name="slicer.util")
_MOCK_SLICER.util = _MOCK_SLICER_UTIL
_MOCK_QT = MagicMock(name="qt")
_MOCK_CTK = MagicMock(name="ctk")
_MOCK_VTK = MagicMock(name="vtk")
_MOCK_SLICER_SCRIPTED = MagicMock(name="slicer.ScriptedLoadableModule")

# Install mocks in sys.modules
sys.modules["slicer"] = _MOCK_SLICER
sys.modules["slicer.util"] = _MOCK_SLICER_UTIL
sys.modules["qt"] = _MOCK_QT
sys.modules["ctk"] = _MOCK_CTK
sys.modules["vtk"] = _MOCK_VTK
sys.modules["slicer.ScriptedLoadableModule"] = _MOCK_SLICER_SCRIPTED


@pytest.fixture(autouse=True)
def reset_slicer_mocks():
    """Reset all Slicer/Qt mocks before each test to ensure isolation."""
    _MOCK_SLICER.reset_mock()
    _MOCK_SLICER_UTIL.reset_mock()
    _MOCK_QT.reset_mock()
    _MOCK_CTK.reset_mock()
    _MOCK_VTK.reset_mock()
    _MOCK_SLICER_SCRIPTED.reset_mock()

    # Re-establish the slicer.util relationship after reset
    _MOCK_SLICER.util = _MOCK_SLICER_UTIL

    yield


def get_mock_slicer():
    """Get the centralized slicer mock."""
    return _MOCK_SLICER


def get_mock_slicer_util():
    """Get the centralized slicer.util mock."""
    return _MOCK_SLICER_UTIL


def get_mock_qt():
    """Get the centralized qt mock."""
    return _MOCK_QT


# =============================================================================
# Pytest markers
# =============================================================================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "requires_slicer: mark test as requiring Slicer environment (skipped in standalone pytest)",
    )


def pytest_collection_modifyitems(config, items):
    """Skip tests marked with requires_slicer when running outside Slicer."""
    # Check if we're running inside real Slicer (not mocked)
    # The real Slicer module has a specific attribute structure
    try:
        import slicer

        # Real Slicer has slicer.mrmlScene which is a vtkMRMLScene, not a MagicMock
        in_slicer = (
            hasattr(slicer, "mrmlScene")
            and not isinstance(slicer.mrmlScene, MagicMock)
            and hasattr(slicer, "app")
            and not isinstance(slicer.app, MagicMock)
        )
    except (ImportError, AttributeError):
        in_slicer = False

    if not in_slicer:
        skip_slicer = pytest.mark.skip(reason="Test requires Slicer environment")
        for item in items:
            if "requires_slicer" in item.keywords:
                item.add_marker(skip_slicer)


@pytest.fixture
def sample_mouse_profile_data() -> dict[str, Any]:
    """Sample mouse profile data for testing."""
    return {
        "id": "test_mouse",
        "name": "Test Mouse",
        "vendor": "Test Vendor",
        "vendorId": "0x1234",
        "productIds": ["0x5678"],
        "buttons": [
            {"id": "left", "name": "Left Click", "qtButton": 1, "remappable": False},
            {"id": "right", "name": "Right Click", "qtButton": 2, "remappable": False},
            {"id": "middle", "name": "Middle Click", "qtButton": 4, "remappable": True},
            {
                "id": "back",
                "name": "Back",
                "qtButton": 8,
                "remappable": True,
                "defaultAction": "edit_undo",
            },
        ],
        "features": {"horizontalScroll": True, "thumbWheel": False},
    }


@pytest.fixture
def sample_preset_data() -> dict[str, Any]:
    """Sample preset data for testing."""
    return {
        "id": "test_preset",
        "name": "Test Preset",
        "version": "1.0",
        "mouseId": "test_mouse",
        "author": "Test Author",
        "description": "A test preset",
        "mappings": {
            "middle": {"action": "view_reset_3d"},
            "back": {"action": "edit_undo"},
        },
        "contextMappings": {
            "SegmentEditor": {
                "back": {"action": "segment_previous"},
            }
        },
    }


@pytest.fixture
def temp_json_file(tmp_path: Path, sample_mouse_profile_data: dict) -> Path:
    """Create a temporary JSON file with sample data."""
    file_path = tmp_path / "test_profile.json"
    with open(file_path, "w") as f:
        json.dump(sample_mouse_profile_data, f)
    return file_path


@pytest.fixture
def temp_preset_file(tmp_path: Path, sample_preset_data: dict) -> Path:
    """Create a temporary preset file."""
    file_path = tmp_path / "test_preset.json"
    with open(file_path, "w") as f:
        json.dump(sample_preset_data, f)
    return file_path


@pytest.fixture
def mock_qt() -> MagicMock:
    """Mock Qt module for testing event handling."""
    qt_mock = MagicMock()
    qt_mock.QEvent.MouseButtonPress = 2
    qt_mock.QEvent.MouseButtonRelease = 3
    qt_mock.LeftButton = 1
    qt_mock.RightButton = 2
    qt_mock.MiddleButton = 4
    qt_mock.BackButton = 8
    qt_mock.ForwardButton = 16
    qt_mock.ShiftModifier = 0x02000000
    qt_mock.ControlModifier = 0x04000000
    qt_mock.AltModifier = 0x08000000
    qt_mock.MetaModifier = 0x10000000
    return qt_mock


@pytest.fixture
def mock_slicer() -> MagicMock:
    """Mock slicer module for testing."""
    slicer_mock = MagicMock()
    slicer_mock.app.moduleManager().currentModule.return_value = "Welcome"
    return slicer_mock


@pytest.fixture
def test_fixtures_dir() -> Path:
    """Path to test fixtures directory."""
    return Path(__file__).parent / "test_fixtures"


class MockMouseEvent:
    """Mock QMouseEvent for testing."""

    def __init__(
        self,
        button: int = 1,
        modifiers: int = 0,
        x: int = 100,
        y: int = 100,
    ):
        self._button = button
        self._modifiers = modifiers
        self._x = x
        self._y = y

    def button(self) -> int:
        return self._button

    def modifiers(self) -> int:
        return self._modifiers

    def x(self) -> int:
        return self._x

    def y(self) -> int:
        return self._y

    def type(self) -> int:
        return 2  # MouseButtonPress


@pytest.fixture
def mock_mouse_event() -> type[MockMouseEvent]:
    """Factory for creating mock mouse events."""
    return MockMouseEvent
