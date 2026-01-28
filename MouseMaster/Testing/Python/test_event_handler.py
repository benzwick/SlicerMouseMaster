"""Tests for MouseMasterEventHandler.

These tests mock Slicer/Qt dependencies to test event handler logic without running inside Slicer.
"""

from unittest.mock import MagicMock, patch

# Import centralized mocks from conftest
from conftest import get_mock_qt, get_mock_slicer, get_mock_slicer_util

# Get local references to mocks (they're reset before each test by conftest fixture)
mock_slicer = get_mock_slicer()
mock_slicer_util = get_mock_slicer_util()
mock_qt = get_mock_qt()


class TestMouseMasterEventHandlerInit:
    """Test MouseMasterEventHandler initialization."""

    def test_init_defaults(self):
        """Test that handler initializes with correct defaults."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()

        assert handler._installed is False
        assert handler._enabled is True
        assert handler._preset is None
        assert handler._qt_handler is None
        assert handler._platform_adapter is None
        assert handler._action_registry is None
        assert handler._on_button_press is None
        assert handler._vtk_observers == []


class TestMouseMasterEventHandlerProperties:
    """Test event handler properties."""

    def test_is_installed_false_by_default(self):
        """Test is_installed returns False initially."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()
        assert handler.is_installed is False

    def test_is_enabled_true_by_default(self):
        """Test is_enabled returns True initially."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()
        assert handler.is_enabled is True

    def test_set_enabled(self):
        """Test set_enabled method."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()
        handler.set_enabled(False)
        assert handler.is_enabled is False
        handler.set_enabled(True)
        assert handler.is_enabled is True


class TestMouseMasterEventHandlerSetPreset:
    """Test preset management."""

    def test_set_preset_stores_preset(self):
        """Test that set_preset stores the preset."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()
        mock_preset = MagicMock()
        mock_preset.name = "Test Preset"

        handler.set_preset(mock_preset)

        assert handler._preset is mock_preset

    def test_set_preset_none(self):
        """Test that set_preset can clear the preset."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()
        mock_preset = MagicMock()
        handler.set_preset(mock_preset)
        handler.set_preset(None)

        assert handler._preset is None


class TestMouseMasterEventHandlerSetOnButtonPress:
    """Test button press callback management."""

    def test_set_on_button_press(self):
        """Test setting the button press callback."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()
        callback = MagicMock()

        handler.set_on_button_press(callback)

        assert handler._on_button_press is callback

    def test_set_on_button_press_none(self):
        """Test clearing the button press callback."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()
        handler.set_on_button_press(MagicMock())
        handler.set_on_button_press(None)

        assert handler._on_button_press is None


class TestMouseMasterEventHandlerInstall:
    """Test install/uninstall functionality."""

    def test_install_sets_installed_flag(self):
        """Test that install sets the installed flag."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()

        with (
            patch("MouseMasterLib.event_handler._create_event_filter") as mock_create,
            patch.object(handler, "_install_vtk_observers"),
        ):
            mock_create.return_value = MagicMock()
            handler.install()

            assert handler.is_installed is True
            assert handler._qt_handler is not None

    def test_install_idempotent(self):
        """Test that calling install twice doesn't install twice."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()

        with (
            patch("MouseMasterLib.event_handler._create_event_filter") as mock_create,
            patch.object(handler, "_install_vtk_observers"),
        ):
            mock_create.return_value = MagicMock()

            handler.install()
            initial_call_count = mock_create.call_count

            handler.install()

            # Should not call create again
            assert mock_create.call_count == initial_call_count

    def test_uninstall_clears_handler(self):
        """Test that uninstall clears the event filter."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()

        with (
            patch("MouseMasterLib.event_handler._create_event_filter") as mock_create,
            patch.object(handler, "_install_vtk_observers"),
        ):
            mock_create.return_value = MagicMock()

            handler.install()
            handler.uninstall()

            assert handler.is_installed is False
            assert handler._qt_handler is None

    def test_uninstall_when_not_installed(self):
        """Test that uninstall does nothing when not installed."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()

        # Should not raise
        handler.uninstall()

        assert handler.is_installed is False


class TestMouseMasterEventHandlerHandleButtonPress:
    """Test handle_button_press method."""

    def test_handle_button_press_disabled_returns_false(self):
        """Test that disabled handler returns False."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()
        handler.set_enabled(False)

        result = handler.handle_button_press(MagicMock())

        assert result is False

    def test_handle_button_press_no_preset_returns_false(self):
        """Test that handler with no preset returns False."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()

        # Mock platform adapter
        mock_adapter = MagicMock()
        mock_normalized = MagicMock()
        mock_normalized.button_id = "back"
        mock_adapter.normalize_event.return_value = mock_normalized

        with patch(
            "MouseMasterLib.platform_adapter.PlatformAdapter.get_instance",
            return_value=mock_adapter,
        ):
            mock_slicer.util.selectedModule.return_value = "Data"
            result = handler.handle_button_press(MagicMock())

        assert result is False

    def test_handle_button_press_no_mapping_returns_false(self):
        """Test that handler with no mapping returns False."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()

        # Set up preset with no mapping
        mock_preset = MagicMock()
        mock_preset.get_mapping.return_value = None
        handler.set_preset(mock_preset)

        # Mock platform adapter
        mock_adapter = MagicMock()
        mock_normalized = MagicMock()
        mock_normalized.button_id = "back"
        mock_adapter.normalize_event.return_value = mock_normalized

        with patch(
            "MouseMasterLib.platform_adapter.PlatformAdapter.get_instance",
            return_value=mock_adapter,
        ):
            mock_slicer.util.selectedModule.return_value = "Data"
            result = handler.handle_button_press(MagicMock())

        assert result is False
        mock_preset.get_mapping.assert_called_once()

    def test_handle_button_press_calls_callback(self):
        """Test that button press callback is called."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()

        callback = MagicMock()
        handler.set_on_button_press(callback)

        # Mock platform adapter
        mock_adapter = MagicMock()
        mock_normalized = MagicMock()
        mock_normalized.button_id = "back"
        mock_adapter.normalize_event.return_value = mock_normalized

        with (
            patch(
                "MouseMasterLib.platform_adapter.PlatformAdapter.get_instance",
                return_value=mock_adapter,
            ),
            patch.object(handler, "_get_current_context", return_value="Data"),
        ):
            handler.handle_button_press(MagicMock())

        callback.assert_called_once_with("back", "Data")

    def test_handle_button_press_with_mapping_returns_true(self):
        """Test that handler with mapping returns True and executes."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()

        # Set up preset with mapping
        mock_mapping = MagicMock()
        mock_mapping.action = "edit_undo"
        mock_mapping.action_id = None
        mock_preset = MagicMock()
        mock_preset.get_mapping.return_value = mock_mapping
        handler.set_preset(mock_preset)

        # Mock platform adapter
        mock_adapter = MagicMock()
        mock_normalized = MagicMock()
        mock_normalized.button_id = "back"
        mock_normalized.modifiers = set()
        mock_adapter.normalize_event.return_value = mock_normalized

        # Mock action registry
        mock_registry = MagicMock()

        with (
            patch(
                "MouseMasterLib.platform_adapter.PlatformAdapter.get_instance",
                return_value=mock_adapter,
            ),
            patch(
                "MouseMasterLib.action_registry.ActionRegistry.get_instance",
                return_value=mock_registry,
            ),
        ):
            mock_slicer.util.selectedModule.return_value = "Data"
            result = handler.handle_button_press(MagicMock())

        assert result is True
        mock_registry.execute.assert_called_once()


class TestMouseMasterEventHandlerExecuteMapping:
    """Test _execute_mapping method."""

    def test_execute_python_command(self):
        """Test executing a Python command mapping."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()

        mock_mapping = MagicMock()
        mock_mapping.action = "python_command"
        mock_mapping.parameters = {"command": "print('test')"}

        mock_normalized = MagicMock()
        mock_normalized.button_id = "back"
        mock_normalized.modifiers = set()

        with patch("MouseMasterLib.action_registry.PythonCommandHandler") as MockPythonHandler:
            mock_handler_instance = MagicMock()
            MockPythonHandler.return_value = mock_handler_instance

            handler._execute_mapping(mock_mapping, mock_normalized, "Data")

            MockPythonHandler.assert_called_once_with("print('test')")
            mock_handler_instance.execute.assert_called_once()

    def test_execute_keyboard_shortcut(self):
        """Test executing a keyboard shortcut mapping."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()

        mock_mapping = MagicMock()
        mock_mapping.action = "keyboard_shortcut"
        mock_mapping.parameters = {"key": "Z", "modifiers": ["ctrl"]}

        mock_normalized = MagicMock()
        mock_normalized.button_id = "back"
        mock_normalized.modifiers = set()

        with patch("MouseMasterLib.action_registry.KeyboardShortcutHandler") as MockKeyboardHandler:
            mock_handler_instance = MagicMock()
            MockKeyboardHandler.return_value = mock_handler_instance

            handler._execute_mapping(mock_mapping, mock_normalized, "Data")

            MockKeyboardHandler.assert_called_once_with("Z", ["ctrl"])
            mock_handler_instance.execute.assert_called_once()

    def test_execute_slicer_action(self):
        """Test executing a Slicer action mapping."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()

        mock_mapping = MagicMock()
        mock_mapping.action = "slicer_action"
        mock_mapping.action_id = "edit_undo"

        mock_normalized = MagicMock()
        mock_normalized.button_id = "back"
        mock_normalized.modifiers = set()

        mock_registry = MagicMock()

        with patch(
            "MouseMasterLib.action_registry.ActionRegistry.get_instance",
            return_value=mock_registry,
        ):
            handler._execute_mapping(mock_mapping, mock_normalized, "Data")

            mock_registry.execute.assert_called_once()
            # Check the action_id was passed
            call_args = mock_registry.execute.call_args
            assert call_args[0][0] == "edit_undo"


class TestInstallVtkObservers:
    """Test VTK observer installation."""

    def test_install_vtk_observers_no_layout_manager(self):
        """Test handling when layout manager is not available."""
        import slicer

        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()
        handler._qt_handler = MagicMock()

        # Configure layoutManager to return None
        slicer.app.layoutManager = MagicMock(return_value=None)

        # Should not raise
        handler._install_vtk_observers()

        assert handler._vtk_observers == []

    def test_install_vtk_observers_with_views(self):
        """Test installing observers on slice and 3D views."""
        import slicer

        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()
        handler._qt_handler = MagicMock()

        # Set up mock layout manager
        mock_layout_manager = MagicMock()
        mock_layout_manager.sliceViewNames.return_value = ["Red", "Green", "Yellow"]
        mock_layout_manager.threeDViewCount = 1

        # Mock slice widgets - each must be unique
        mock_slice_views = [MagicMock(name=f"slice_view_{i}") for i in range(3)]
        mock_slice_widgets = []
        for view in mock_slice_views:
            widget = MagicMock()
            widget.sliceView.return_value = view
            mock_slice_widgets.append(widget)

        mock_layout_manager.sliceWidget.side_effect = mock_slice_widgets

        # Mock 3D widget
        mock_3d_view = MagicMock(name="3d_view")
        mock_3d_widget = MagicMock()
        mock_3d_widget.threeDView.return_value = mock_3d_view
        mock_layout_manager.threeDWidget.return_value = mock_3d_widget

        slicer.app.layoutManager = MagicMock(return_value=mock_layout_manager)

        handler._install_vtk_observers()

        # Should have 3 slice views + 1 3D view = 4 observers
        assert len(handler._vtk_observers) == 4


class TestCreateEventFilter:
    """Test _create_event_filter function."""

    def test_create_event_filter_returns_object(self):
        """Test that _create_event_filter returns a Qt object."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler, _create_event_filter

        handler = MouseMasterEventHandler()

        # Mock qt.QObject
        mock_qt.QObject = MagicMock()
        mock_qt.QEvent.MouseButtonPress = 2
        mock_qt.QEvent.MouseButtonRelease = 3

        filter_obj = _create_event_filter(handler)

        assert filter_obj is not None


class TestGetCurrentContext:
    """Test _get_current_context method."""

    def test_get_current_context_returns_module_name(self):
        """Test getting current module context."""
        import slicer.util

        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()

        # Configure the mock directly
        slicer.util.selectedModule = MagicMock(return_value="SegmentEditor")
        context = handler._get_current_context()

        assert context == "SegmentEditor"

    def test_get_current_context_returns_default_when_none(self):
        """Test that default context is returned when no module selected."""
        import slicer.util

        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()

        # Configure the mock to return None
        slicer.util.selectedModule = MagicMock(return_value=None)
        context = handler._get_current_context()

        assert context == "default"


class TestUninstallWithRuntimeError:
    """Test uninstall handling RuntimeError from deleted views."""

    def test_uninstall_handles_deleted_view(self):
        """Test that uninstall handles RuntimeError from deleted view widgets."""
        from MouseMasterLib.event_handler import MouseMasterEventHandler

        handler = MouseMasterEventHandler()

        # Simulate installed state with views
        handler._installed = True
        mock_qt_handler = MagicMock()
        handler._qt_handler = mock_qt_handler

        # Create a mock view that raises RuntimeError when removing filter
        mock_view = MagicMock()
        mock_view.removeEventFilter.side_effect = RuntimeError("Widget deleted")
        handler._vtk_observers = [(mock_view, "filter")]

        # Should not raise
        handler.uninstall()

        assert handler.is_installed is False
        assert handler._vtk_observers == []
        assert handler._qt_handler is None
