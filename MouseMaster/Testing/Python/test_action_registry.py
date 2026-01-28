"""Tests for ActionRegistry.

These tests mock Slicer/Qt dependencies to test action registry logic without running inside Slicer.
"""

import pytest
from unittest.mock import MagicMock, patch

# Import centralized mocks from conftest
from conftest import get_mock_slicer, get_mock_slicer_util, get_mock_qt

# Get local references to mocks (they're reset before each test by conftest fixture)
mock_slicer = get_mock_slicer()
mock_slicer_util = get_mock_slicer_util()
mock_qt = get_mock_qt()


class TestActionContext:
    """Test ActionContext dataclass."""

    def test_default_values(self):
        """Test ActionContext default values."""
        from MouseMasterLib.action_registry import ActionContext

        context = ActionContext()

        assert context.module_name is None
        assert context.button_id is None
        assert context.modifiers == set()
        assert context.view_name is None

    def test_with_values(self):
        """Test ActionContext with provided values."""
        from MouseMasterLib.action_registry import ActionContext

        context = ActionContext(
            module_name="SegmentEditor",
            button_id="back",
            modifiers={"ctrl", "shift"},
            view_name="Red",
        )

        assert context.module_name == "SegmentEditor"
        assert context.button_id == "back"
        assert context.modifiers == {"ctrl", "shift"}
        assert context.view_name == "Red"


class TestActionEntry:
    """Test ActionEntry dataclass."""

    def test_action_entry_fields(self):
        """Test ActionEntry fields."""
        from MouseMasterLib.action_registry import ActionEntry, CallableHandler

        handler = CallableHandler(lambda ctx: True)
        entry = ActionEntry(
            id="test_action",
            handler=handler,
            category="test",
            description="Test action",
            icon="test-icon",
        )

        assert entry.id == "test_action"
        assert entry.handler is handler
        assert entry.category == "test"
        assert entry.description == "Test action"
        assert entry.icon == "test-icon"

    def test_action_entry_optional_icon(self):
        """Test ActionEntry with default None icon."""
        from MouseMasterLib.action_registry import ActionEntry, CallableHandler

        handler = CallableHandler(lambda ctx: True)
        entry = ActionEntry(
            id="test_action",
            handler=handler,
            category="test",
            description="Test action",
        )

        assert entry.icon is None


class TestCallableHandler:
    """Test CallableHandler."""

    def test_execute_calls_function(self):
        """Test that execute calls the wrapped function."""
        from MouseMasterLib.action_registry import CallableHandler, ActionContext

        called = []

        def test_func(ctx):
            called.append(ctx)
            return True

        handler = CallableHandler(test_func)
        context = ActionContext(module_name="Test")

        result = handler.execute(context)

        assert result is True
        assert len(called) == 1
        assert called[0] is context

    def test_is_available_default_true(self):
        """Test that is_available returns True by default."""
        from MouseMasterLib.action_registry import CallableHandler, ActionContext

        handler = CallableHandler(lambda ctx: True)
        context = ActionContext()

        assert handler.is_available(context) is True

    def test_is_available_with_check(self):
        """Test is_available with custom check function."""
        from MouseMasterLib.action_registry import CallableHandler, ActionContext

        handler = CallableHandler(
            lambda ctx: True, available_check=lambda ctx: ctx.module_name == "SegmentEditor"
        )

        assert handler.is_available(ActionContext(module_name="SegmentEditor")) is True
        assert handler.is_available(ActionContext(module_name="Data")) is False


class TestSlicerActionHandler:
    """Test SlicerActionHandler."""

    def test_execute_triggers_action(self):
        """Test that execute triggers the Slicer menu action."""
        from MouseMasterLib.action_registry import SlicerActionHandler, ActionContext

        # Set up mock action
        mock_action = MagicMock()
        mock_main_window = MagicMock()
        mock_main_window.findChild.return_value = mock_action

        # Configure the mock at the module level
        mock_slicer_util.mainWindow.return_value = mock_main_window

        handler = SlicerActionHandler("actionUndo")
        context = ActionContext()

        result = handler.execute(context)

        assert result is True
        mock_action.trigger.assert_called_once()

    def test_execute_no_main_window(self):
        """Test execute when main window is not available."""
        from MouseMasterLib.action_registry import SlicerActionHandler, ActionContext

        mock_slicer_util.mainWindow.return_value = None

        handler = SlicerActionHandler("actionUndo")
        context = ActionContext()

        result = handler.execute(context)

        assert result is False

    def test_execute_action_not_found(self):
        """Test execute when action is not found."""
        from MouseMasterLib.action_registry import SlicerActionHandler, ActionContext

        mock_main_window = MagicMock()
        mock_main_window.findChild.return_value = None
        mock_slicer_util.mainWindow.return_value = mock_main_window

        handler = SlicerActionHandler("nonexistentAction")
        context = ActionContext()

        result = handler.execute(context)

        assert result is False


class TestPythonCommandHandler:
    """Test PythonCommandHandler."""

    def test_execute_returns_true(self):
        """Test that execute returns True on success."""
        from MouseMasterLib.action_registry import PythonCommandHandler, ActionContext

        # Simple command that just passes
        handler = PythonCommandHandler("pass")
        context = ActionContext()

        result = handler.execute(context)

        assert result is True

    def test_execute_has_slicer_available(self):
        """Test that slicer is available in the command namespace."""
        from MouseMasterLib.action_registry import PythonCommandHandler, ActionContext

        # Command that uses slicer - this verifies slicer is in namespace
        handler = PythonCommandHandler("x = slicer")
        context = ActionContext()

        # Should not raise
        result = handler.execute(context)
        assert result is True

    def test_execute_has_context_available(self):
        """Test that context is available in the command namespace."""
        from MouseMasterLib.action_registry import PythonCommandHandler, ActionContext

        # Command that accesses context
        handler = PythonCommandHandler("x = context.module_name")
        context = ActionContext(module_name="TestModule")

        # Should not raise
        result = handler.execute(context)
        assert result is True


class TestKeyboardShortcutHandler:
    """Test KeyboardShortcutHandler."""

    def test_init_with_modifiers(self):
        """Test initialization with modifiers."""
        from MouseMasterLib.action_registry import KeyboardShortcutHandler

        handler = KeyboardShortcutHandler("Z", ["ctrl", "shift"])

        assert handler._key == "Z"
        assert handler._modifiers == ["ctrl", "shift"]

    def test_init_without_modifiers(self):
        """Test initialization without modifiers."""
        from MouseMasterLib.action_registry import KeyboardShortcutHandler

        handler = KeyboardShortcutHandler("A")

        assert handler._key == "A"
        assert handler._modifiers == []

    def test_execute_posts_key_event(self):
        """Test that execute posts a key event."""
        from MouseMasterLib.action_registry import KeyboardShortcutHandler, ActionContext

        # Set up mocks
        mock_main_window = MagicMock()
        mock_focus_widget = MagicMock()
        mock_main_window.focusWidget.return_value = mock_focus_widget
        mock_slicer_util.mainWindow.return_value = mock_main_window

        mock_qt.Qt.NoModifier = 0
        mock_qt.Qt.ControlModifier = 1
        mock_qt.Qt.Key_Z = 90
        mock_qt.QEvent.KeyPress = 6

        handler = KeyboardShortcutHandler("Z", ["ctrl"])
        context = ActionContext()

        result = handler.execute(context)

        assert result is True
        mock_qt.QApplication.postEvent.assert_called_once()

    def test_execute_no_main_window(self):
        """Test execute when main window is not available."""
        from MouseMasterLib.action_registry import KeyboardShortcutHandler, ActionContext

        mock_slicer_util.mainWindow.return_value = None

        handler = KeyboardShortcutHandler("Z")
        context = ActionContext()

        result = handler.execute(context)

        assert result is False

    def test_execute_unknown_key(self):
        """Test execute with unknown key."""
        from MouseMasterLib.action_registry import KeyboardShortcutHandler, ActionContext

        mock_main_window = MagicMock()
        mock_slicer_util.mainWindow.return_value = mock_main_window
        mock_qt.Qt.NoModifier = 0

        # Delete any existing Key_UnknownKey and Key_UNKNOWNKEY attributes
        for attr in ["Key_UnknownKey", "Key_UNKNOWNKEY"]:
            if hasattr(mock_qt.Qt, attr):
                delattr(mock_qt.Qt, attr)

        handler = KeyboardShortcutHandler("UnknownKey")
        context = ActionContext()

        result = handler.execute(context)

        assert result is False


class TestActionRegistry:
    """Test ActionRegistry singleton and methods."""

    def setup_method(self):
        """Reset singleton before each test."""
        from MouseMasterLib.action_registry import ActionRegistry

        ActionRegistry.reset_instance()

    def test_get_instance_returns_singleton(self):
        """Test that get_instance returns the same instance."""
        from MouseMasterLib.action_registry import ActionRegistry

        instance1 = ActionRegistry.get_instance()
        instance2 = ActionRegistry.get_instance()

        assert instance1 is instance2

    def test_reset_instance_clears_singleton(self):
        """Test that reset_instance clears the singleton."""
        from MouseMasterLib.action_registry import ActionRegistry

        instance1 = ActionRegistry.get_instance()
        ActionRegistry.reset_instance()
        instance2 = ActionRegistry.get_instance()

        assert instance1 is not instance2

    def test_register_action(self):
        """Test registering an action."""
        from MouseMasterLib.action_registry import ActionRegistry, CallableHandler

        registry = ActionRegistry()
        handler = CallableHandler(lambda ctx: True)

        registry.register(
            "test_action", handler, "test_category", "Test description", "test-icon"
        )

        assert "test_action" in registry._actions
        entry = registry._actions["test_action"]
        assert entry.id == "test_action"
        assert entry.handler is handler
        assert entry.category == "test_category"
        assert entry.description == "Test description"
        assert entry.icon == "test-icon"

    def test_register_adds_to_category(self):
        """Test that register adds action to category list."""
        from MouseMasterLib.action_registry import ActionRegistry, CallableHandler

        registry = ActionRegistry()
        handler = CallableHandler(lambda ctx: True)

        registry.register("action1", handler, "category1", "Action 1")
        registry.register("action2", handler, "category1", "Action 2")
        registry.register("action3", handler, "category2", "Action 3")

        assert "action1" in registry._categories["category1"]
        assert "action2" in registry._categories["category1"]
        assert "action3" in registry._categories["category2"]

    def test_unregister_action(self):
        """Test unregistering an action."""
        from MouseMasterLib.action_registry import ActionRegistry, CallableHandler

        registry = ActionRegistry()
        handler = CallableHandler(lambda ctx: True)
        registry.register("test_action", handler, "test_category", "Test")

        result = registry.unregister("test_action")

        assert result is True
        assert "test_action" not in registry._actions
        assert "test_action" not in registry._categories.get("test_category", [])

    def test_unregister_nonexistent(self):
        """Test unregistering a nonexistent action."""
        from MouseMasterLib.action_registry import ActionRegistry

        registry = ActionRegistry()

        result = registry.unregister("nonexistent")

        assert result is False

    def test_get_action(self):
        """Test getting an action by ID."""
        from MouseMasterLib.action_registry import ActionRegistry, CallableHandler

        registry = ActionRegistry()
        handler = CallableHandler(lambda ctx: True)
        registry.register("test_action", handler, "test_category", "Test")

        entry = registry.get_action("test_action")

        assert entry is not None
        assert entry.id == "test_action"

    def test_get_action_not_found(self):
        """Test getting a nonexistent action."""
        from MouseMasterLib.action_registry import ActionRegistry

        registry = ActionRegistry()

        entry = registry.get_action("nonexistent")

        assert entry is None

    def test_execute_action(self):
        """Test executing an action."""
        from MouseMasterLib.action_registry import ActionRegistry, CallableHandler, ActionContext

        executed = []

        def handler_func(ctx):
            executed.append(ctx)
            return True

        registry = ActionRegistry()
        handler = CallableHandler(handler_func)
        registry.register("test_action", handler, "test_category", "Test")

        context = ActionContext(module_name="Test")
        result = registry.execute("test_action", context)

        assert result is True
        assert len(executed) == 1

    def test_execute_nonexistent_action(self):
        """Test executing a nonexistent action."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        registry = ActionRegistry()
        context = ActionContext()

        result = registry.execute("nonexistent", context)

        assert result is False

    def test_execute_unavailable_action(self):
        """Test executing an unavailable action."""
        from MouseMasterLib.action_registry import ActionRegistry, CallableHandler, ActionContext

        registry = ActionRegistry()
        handler = CallableHandler(lambda ctx: True, available_check=lambda ctx: False)
        registry.register("test_action", handler, "test_category", "Test")

        context = ActionContext()
        result = registry.execute("test_action", context)

        assert result is False

    def test_get_actions_by_category(self):
        """Test getting actions by category."""
        from MouseMasterLib.action_registry import ActionRegistry, CallableHandler

        registry = ActionRegistry()
        handler = CallableHandler(lambda ctx: True)
        registry.register("action1", handler, "category1", "Action 1")
        registry.register("action2", handler, "category1", "Action 2")
        registry.register("action3", handler, "category2", "Action 3")

        actions = registry.get_actions_by_category("category1")

        assert len(actions) == 2
        assert all(a.category == "category1" for a in actions)

    def test_get_actions_by_nonexistent_category(self):
        """Test getting actions by nonexistent category."""
        from MouseMasterLib.action_registry import ActionRegistry

        registry = ActionRegistry()

        actions = registry.get_actions_by_category("nonexistent")

        assert actions == []

    def test_get_categories(self):
        """Test getting all categories."""
        from MouseMasterLib.action_registry import ActionRegistry, CallableHandler

        registry = ActionRegistry()
        handler = CallableHandler(lambda ctx: True)
        registry.register("action1", handler, "category1", "Action 1")
        registry.register("action2", handler, "category2", "Action 2")

        categories = registry.get_categories()

        assert "category1" in categories
        assert "category2" in categories

    def test_get_all_actions(self):
        """Test getting all actions."""
        from MouseMasterLib.action_registry import ActionRegistry, CallableHandler

        registry = ActionRegistry()
        handler = CallableHandler(lambda ctx: True)
        registry.register("action1", handler, "category1", "Action 1")
        registry.register("action2", handler, "category2", "Action 2")

        actions = registry.get_all_actions()

        assert len(actions) == 2


class TestActionRegistryBuiltinActions:
    """Test built-in action registration."""

    def setup_method(self):
        """Reset singleton before each test."""
        from MouseMasterLib.action_registry import ActionRegistry

        ActionRegistry.reset_instance()

    def test_get_instance_registers_builtin_actions(self):
        """Test that get_instance registers built-in actions."""
        from MouseMasterLib.action_registry import ActionRegistry

        registry = ActionRegistry.get_instance()

        # Check some known built-in actions exist
        assert registry.get_action("edit_undo") is not None
        assert registry.get_action("edit_redo") is not None
        assert registry.get_action("view_reset_3d") is not None
        assert registry.get_action("segment_editor_paint") is not None

    def test_builtin_actions_have_correct_categories(self):
        """Test that built-in actions have correct categories."""
        from MouseMasterLib.action_registry import ActionRegistry

        registry = ActionRegistry.get_instance()

        assert registry.get_action("edit_undo").category == "editing"
        assert registry.get_action("view_reset_3d").category == "navigation"
        assert registry.get_action("segment_editor_paint").category == "segment_editor"


class TestDiscoverSlicerActions:
    """Test discover_slicer_actions method."""

    def setup_method(self):
        """Reset singleton before each test."""
        from MouseMasterLib.action_registry import ActionRegistry

        ActionRegistry.reset_instance()

    def test_discover_actions_no_main_window(self):
        """Test discovery when main window is not available."""
        from MouseMasterLib.action_registry import ActionRegistry

        mock_slicer_util.mainWindow.return_value = None

        registry = ActionRegistry()
        count = registry.discover_slicer_actions()

        assert count == 0

    def test_discover_actions_with_actions(self):
        """Test discovering actions from main window."""
        from MouseMasterLib.action_registry import ActionRegistry

        # Set up mock main window with actions
        mock_main = MagicMock()
        mock_action = MagicMock()
        mock_action.objectName = "actionTest"
        mock_action.text = "Test Action"
        mock_action.isSeparator = False
        mock_action.parent.return_value = None
        mock_main.findChildren.return_value = [mock_action]
        mock_slicer_util.mainWindow.return_value = mock_main

        registry = ActionRegistry()
        count = registry.discover_slicer_actions()

        assert count == 1
        assert registry.get_action("slicer_menu_actionTest") is not None

    def test_discover_actions_skips_duplicates(self):
        """Test that discovery skips already registered actions."""
        from MouseMasterLib.action_registry import ActionRegistry, CallableHandler

        # Pre-register an action
        registry = ActionRegistry()
        registry.register(
            "slicer_menu_actionTest",
            CallableHandler(lambda ctx: True),
            "test",
            "Test",
        )

        # Set up mock with same action
        mock_main = MagicMock()
        mock_action = MagicMock()
        mock_action.objectName = "actionTest"
        mock_action.text = "Test Action"
        mock_action.isSeparator = False
        mock_action.parent.return_value = None
        mock_main.findChildren.return_value = [mock_action]
        mock_slicer_util.mainWindow.return_value = mock_main

        count = registry.discover_slicer_actions()

        assert count == 0  # Should not register duplicate

    def test_discover_actions_skips_separators(self):
        """Test that discovery skips separator actions."""
        from MouseMasterLib.action_registry import ActionRegistry

        mock_main = MagicMock()
        mock_action = MagicMock()
        mock_action.objectName = "separator"
        mock_action.text = ""
        mock_action.isSeparator = True
        mock_main.findChildren.return_value = [mock_action]
        mock_slicer_util.mainWindow.return_value = mock_main

        registry = ActionRegistry()
        count = registry.discover_slicer_actions()

        assert count == 0


class TestBuiltinActionImplementations:
    """Test built-in action handler implementations."""

    def setup_method(self):
        """Reset singleton and mocks before each test."""
        from MouseMasterLib.action_registry import ActionRegistry

        ActionRegistry.reset_instance()
        mock_slicer.reset_mock()
        mock_slicer_util.reset_mock()

    def test_do_undo_segment_editor(self):
        """Test undo in SegmentEditor context."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        mock_editor = MagicMock()
        mock_widget_self = MagicMock()
        mock_widget_self.editor = mock_editor
        mock_widget = MagicMock()
        mock_widget.self.return_value = mock_widget_self

        mock_slicer.modules.segmenteditor.widgetRepresentation.return_value = mock_widget

        context = ActionContext(module_name="SegmentEditor")
        result = ActionRegistry._do_undo(context)

        assert result is True
        mock_editor.undo.assert_called_once()

    def test_do_undo_other_module(self):
        """Test undo in non-SegmentEditor context."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        mock_slicer.reset_mock()
        context = ActionContext(module_name="Data")
        result = ActionRegistry._do_undo(context)

        assert result is True
        mock_slicer.mrmlScene.Undo.assert_called_once()

    def test_do_redo_segment_editor(self):
        """Test redo in SegmentEditor context."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        mock_editor = MagicMock()
        mock_widget_self = MagicMock()
        mock_widget_self.editor = mock_editor
        mock_widget = MagicMock()
        mock_widget.self.return_value = mock_widget_self

        mock_slicer.modules.segmenteditor.widgetRepresentation.return_value = mock_widget

        context = ActionContext(module_name="SegmentEditor")
        result = ActionRegistry._do_redo(context)

        assert result is True
        mock_editor.redo.assert_called_once()

    def test_do_redo_other_module(self):
        """Test redo in non-SegmentEditor context."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        mock_slicer.reset_mock()
        context = ActionContext(module_name="Data")
        result = ActionRegistry._do_redo(context)

        assert result is True
        mock_slicer.mrmlScene.Redo.assert_called_once()

    def test_reset_3d_view(self):
        """Test reset 3D view."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        mock_view = MagicMock()
        mock_widget = MagicMock()
        mock_widget.threeDView.return_value = mock_view

        mock_layout_manager = MagicMock()
        mock_layout_manager.threeDViewCount = 1
        mock_layout_manager.threeDWidget.return_value = mock_widget

        mock_slicer.app.layoutManager.return_value = mock_layout_manager

        context = ActionContext()
        result = ActionRegistry._reset_3d_view(context)

        assert result is True
        mock_view.resetFocalPoint.assert_called_once()
        mock_view.resetCamera.assert_called_once()

    def test_toggle_crosshair(self):
        """Test toggle crosshair."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        mock_crosshair = MagicMock()
        mock_crosshair.GetCrosshairMode.return_value = 0
        mock_slicer_util.getNode.return_value = mock_crosshair

        context = ActionContext()
        result = ActionRegistry._toggle_crosshair(context)

        assert result is True
        mock_crosshair.SetCrosshairMode.assert_called_once()

    def test_is_segment_editor_active(self):
        """Test segment editor context check."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        assert ActionRegistry._is_segment_editor_active(ActionContext(module_name="SegmentEditor")) is True
        assert ActionRegistry._is_segment_editor_active(ActionContext(module_name="Data")) is False

    def test_is_markups_active(self):
        """Test markups context check."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        assert ActionRegistry._is_markups_active(ActionContext(module_name="Markups")) is True
        assert ActionRegistry._is_markups_active(ActionContext(module_name="Data")) is False

    def test_next_segment(self):
        """Test next segment selection."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        # Set up mock segmentation
        mock_seg = MagicMock()
        mock_seg.GetNumberOfSegments.return_value = 3
        mock_seg.GetNthSegmentID.side_effect = lambda i: f"segment_{i}"

        mock_segmentation = MagicMock()
        mock_segmentation.GetSegmentation.return_value = mock_seg

        mock_editor = MagicMock()
        mock_editor.segmentationNode.return_value = mock_segmentation
        mock_editor.currentSegmentID.return_value = "segment_0"

        mock_widget_self = MagicMock()
        mock_widget_self.editor = mock_editor
        mock_widget = MagicMock()
        mock_widget.self.return_value = mock_widget_self

        mock_slicer.modules.segmenteditor.widgetRepresentation.return_value = mock_widget

        context = ActionContext(module_name="SegmentEditor")
        result = ActionRegistry._next_segment(context)

        assert result is True
        mock_editor.setCurrentSegmentID.assert_called_once_with("segment_1")

    def test_previous_segment(self):
        """Test previous segment selection."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        # Set up mock segmentation
        mock_seg = MagicMock()
        mock_seg.GetNumberOfSegments.return_value = 3
        mock_seg.GetNthSegmentID.side_effect = lambda i: f"segment_{i}"

        mock_segmentation = MagicMock()
        mock_segmentation.GetSegmentation.return_value = mock_seg

        mock_editor = MagicMock()
        mock_editor.segmentationNode.return_value = mock_segmentation
        mock_editor.currentSegmentID.return_value = "segment_1"

        mock_widget_self = MagicMock()
        mock_widget_self.editor = mock_editor
        mock_widget = MagicMock()
        mock_widget.self.return_value = mock_widget_self

        mock_slicer.modules.segmenteditor.widgetRepresentation.return_value = mock_widget

        context = ActionContext(module_name="SegmentEditor")
        result = ActionRegistry._previous_segment(context)

        assert result is True
        mock_editor.setCurrentSegmentID.assert_called_once_with("segment_0")

    def test_add_segment(self):
        """Test adding a new segment."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        mock_seg = MagicMock()
        mock_seg.AddEmptySegment.return_value = "new_segment_id"

        mock_segmentation = MagicMock()
        mock_segmentation.GetSegmentation.return_value = mock_seg

        mock_editor = MagicMock()
        mock_editor.segmentationNode.return_value = mock_segmentation

        mock_widget_self = MagicMock()
        mock_widget_self.editor = mock_editor
        mock_widget = MagicMock()
        mock_widget.self.return_value = mock_widget_self

        mock_slicer.modules.segmenteditor.widgetRepresentation.return_value = mock_widget

        context = ActionContext(module_name="SegmentEditor")
        result = ActionRegistry._add_segment(context)

        assert result is True
        mock_seg.AddEmptySegment.assert_called_once()
        mock_editor.setCurrentSegmentID.assert_called_once_with("new_segment_id")

    def test_place_fiducial(self):
        """Test placing fiducial."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        mock_interaction = MagicMock()
        mock_interaction.Place = 1
        mock_selection = MagicMock()

        mock_app_logic = MagicMock()
        mock_app_logic.GetInteractionNode.return_value = mock_interaction
        mock_app_logic.GetSelectionNode.return_value = mock_selection

        mock_slicer.app.applicationLogic.return_value = mock_app_logic

        context = ActionContext(module_name="Markups")
        result = ActionRegistry._place_fiducial(context)

        assert result is True
        mock_selection.SetReferenceActivePlaceNodeClassName.assert_called_once()
        mock_interaction.SetCurrentInteractionMode.assert_called_once()

    def test_delete_markup_point(self):
        """Test deleting a markup point."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        mock_markup = MagicMock()
        mock_markup.GetNumberOfControlPoints.return_value = 5

        mock_selection = MagicMock()
        mock_selection.GetActivePlaceNodeID.return_value = "markup_id"

        mock_app_logic = MagicMock()
        mock_app_logic.GetSelectionNode.return_value = mock_selection

        mock_slicer.app.applicationLogic.return_value = mock_app_logic
        mock_slicer.mrmlScene.GetNodeByID.return_value = mock_markup

        context = ActionContext(module_name="Markups")
        result = ActionRegistry._delete_markup_point(context)

        assert result is True
        mock_markup.RemoveNthControlPoint.assert_called_once_with(4)

    def test_delete_markup_point_no_active_node(self):
        """Test deleting markup point when no active node."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        mock_selection = MagicMock()
        mock_selection.GetActivePlaceNodeID.return_value = ""

        mock_app_logic = MagicMock()
        mock_app_logic.GetSelectionNode.return_value = mock_selection

        mock_slicer.app.applicationLogic.return_value = mock_app_logic

        context = ActionContext(module_name="Markups")
        result = ActionRegistry._delete_markup_point(context)

        assert result is False

    def test_toggle_volume_rendering(self):
        """Test toggling volume rendering."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        mock_node = MagicMock()
        mock_node.GetVisibility.return_value = True
        mock_slicer_util.getNodesByClass.return_value = [mock_node]

        context = ActionContext()
        result = ActionRegistry._toggle_volume_rendering(context)

        assert result is True
        mock_node.SetVisibility.assert_called_once_with(False)


class TestSetSegmentEditorEffect:
    """Test _set_segment_editor_effect factory method."""

    def setup_method(self):
        """Reset mocks before each test."""
        mock_slicer.reset_mock()

    def test_creates_handler_function(self):
        """Test that factory creates a working handler."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        mock_editor = MagicMock()
        mock_widget_self = MagicMock()
        mock_widget_self.editor = mock_editor
        mock_widget = MagicMock()
        mock_widget.self.return_value = mock_widget_self

        mock_slicer.modules.segmenteditor.widgetRepresentation.return_value = mock_widget

        handler_func = ActionRegistry._set_segment_editor_effect("Paint")
        context = ActionContext(module_name="SegmentEditor")

        result = handler_func(context)

        assert result is True
        mock_editor.setActiveEffectByName.assert_called_once_with("Paint")

    def test_returns_false_when_no_widget(self):
        """Test handler returns False when editor widget unavailable."""
        from MouseMasterLib.action_registry import ActionRegistry, ActionContext

        mock_slicer.modules.segmenteditor.widgetRepresentation.return_value = None

        handler_func = ActionRegistry._set_segment_editor_effect("Paint")
        context = ActionContext(module_name="SegmentEditor")

        result = handler_func(context)

        assert result is False
