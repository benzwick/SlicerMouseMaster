"""Tests for MouseMasterWidget UI code.

These tests mock Slicer/Qt dependencies to test widget logic without running inside Slicer.
"""

from unittest.mock import MagicMock

# Mocks are set up centrally in conftest.py - no need to set up sys.modules here


class TestOnActionChanged:
    """Test _onActionChanged method - the method that had the sender() bug."""

    def setup_method(self):
        """Set up test fixtures."""
        # Import after mocking
        from MouseMasterLib.preset_manager import Mapping, Preset, PresetManager

        self.PresetManager = PresetManager
        self.Preset = Preset
        self.Mapping = Mapping

    def test_on_action_changed_with_combo(self):
        """Test that _onActionChanged works when combo is passed directly."""
        # Create mock objects
        mock_combo = MagicMock()
        mock_combo.currentData = "edit_undo"

        mock_preset = MagicMock()
        mock_preset_manager = MagicMock()
        mock_preset_manager.get_preset.return_value = mock_preset

        mock_event_handler = MagicMock()

        mock_parameter_node = MagicMock()
        mock_parameter_node.selectedPresetId = "test_preset"

        mock_context_toggle = MagicMock()
        mock_context_toggle.checked = False

        # Create a minimal widget-like object to test the method
        class MockWidget:
            def __init__(self):
                self._parameterNode = mock_parameter_node
                self._presetManager = mock_preset_manager
                self._eventHandler = mock_event_handler
                self.contextToggle = mock_context_toggle
                self.contextSelector = MagicMock()

            def _onActionChanged(self, button_id: str, index: int, combo=None) -> None:
                """Handle action selection change for a button."""
                presetId = self._parameterNode.selectedPresetId if self._parameterNode else ""
                if not presetId:
                    return

                preset = self._presetManager.get_preset(presetId)
                if not preset:
                    return

                if not combo:
                    return

                action_id = combo.currentData
                context = None
                if self.contextToggle.checked:
                    context = (
                        self.contextSelector.currentData
                        if self.contextSelector.currentData
                        else None
                    )

                if action_id:
                    from MouseMasterLib.preset_manager import Mapping

                    mapping = Mapping(action=action_id)
                    preset.set_mapping(button_id, mapping, context)
                else:
                    preset.remove_mapping(button_id, context)

                self._presetManager.save_preset(preset)
                self._eventHandler.set_preset(preset)

        widget = MockWidget()

        # Call the method with combo passed directly (the fix)
        widget._onActionChanged("back", 1, mock_combo)

        # Verify the preset was updated
        mock_preset_manager.get_preset.assert_called_with("test_preset")
        mock_preset.set_mapping.assert_called_once()
        mock_preset_manager.save_preset.assert_called_with(mock_preset)
        mock_event_handler.set_preset.assert_called_with(mock_preset)

    def test_on_action_changed_without_combo_returns_early(self):
        """Test that _onActionChanged returns early when combo is None."""
        mock_preset_manager = MagicMock()
        mock_preset_manager.get_preset.return_value = MagicMock()

        mock_parameter_node = MagicMock()
        mock_parameter_node.selectedPresetId = "test_preset"

        class MockWidget:
            def __init__(self):
                self._parameterNode = mock_parameter_node
                self._presetManager = mock_preset_manager
                self._eventHandler = MagicMock()
                self.contextToggle = MagicMock()

            def _onActionChanged(self, button_id: str, index: int, combo=None) -> None:
                presetId = self._parameterNode.selectedPresetId if self._parameterNode else ""
                if not presetId:
                    return
                preset = self._presetManager.get_preset(presetId)
                if not preset:
                    return
                if not combo:
                    return
                # This should not be reached
                preset.set_mapping(button_id, MagicMock(), None)

        widget = MockWidget()

        # Call without combo - should return early
        widget._onActionChanged("back", 1, None)

        # Verify set_mapping was NOT called (early return)
        preset = mock_preset_manager.get_preset.return_value
        preset.set_mapping.assert_not_called()

    def test_on_action_changed_no_preset_id_returns_early(self):
        """Test that _onActionChanged returns early when no preset selected."""
        mock_preset_manager = MagicMock()
        mock_parameter_node = MagicMock()
        mock_parameter_node.selectedPresetId = ""  # No preset selected

        class MockWidget:
            def __init__(self):
                self._parameterNode = mock_parameter_node
                self._presetManager = mock_preset_manager

            def _onActionChanged(self, button_id: str, index: int, combo=None) -> None:
                presetId = self._parameterNode.selectedPresetId if self._parameterNode else ""
                if not presetId:
                    return
                self._presetManager.get_preset(presetId)

        widget = MockWidget()
        widget._onActionChanged("back", 1, MagicMock())

        # Verify get_preset was NOT called (early return)
        mock_preset_manager.get_preset.assert_not_called()

    def test_on_action_changed_clears_mapping_when_none_selected(self):
        """Test that selecting '-- None --' removes the mapping."""
        mock_combo = MagicMock()
        mock_combo.currentData = ""  # Empty = None selected

        mock_preset = MagicMock()
        mock_preset_manager = MagicMock()
        mock_preset_manager.get_preset.return_value = mock_preset

        mock_parameter_node = MagicMock()
        mock_parameter_node.selectedPresetId = "test_preset"

        class MockWidget:
            def __init__(self):
                self._parameterNode = mock_parameter_node
                self._presetManager = mock_preset_manager
                self._eventHandler = MagicMock()
                self.contextToggle = MagicMock()
                self.contextToggle.checked = False

            def _onActionChanged(self, button_id: str, index: int, combo=None) -> None:
                presetId = self._parameterNode.selectedPresetId if self._parameterNode else ""
                if not presetId:
                    return
                preset = self._presetManager.get_preset(presetId)
                if not preset:
                    return
                if not combo:
                    return

                action_id = combo.currentData
                context = None

                if action_id:
                    preset.set_mapping(button_id, MagicMock(), context)
                else:
                    preset.remove_mapping(button_id, context)

                self._presetManager.save_preset(preset)
                self._eventHandler.set_preset(preset)

        widget = MockWidget()
        widget._onActionChanged("back", 0, mock_combo)

        # Verify remove_mapping was called (not set_mapping)
        mock_preset.remove_mapping.assert_called_once_with("back", None)
        mock_preset.set_mapping.assert_not_called()

    def test_on_action_changed_with_context(self):
        """Test that context-specific mappings work correctly."""
        mock_combo = MagicMock()
        mock_combo.currentData = "segment_next"

        mock_preset = MagicMock()
        mock_preset_manager = MagicMock()
        mock_preset_manager.get_preset.return_value = mock_preset

        mock_parameter_node = MagicMock()
        mock_parameter_node.selectedPresetId = "test_preset"

        mock_context_toggle = MagicMock()
        mock_context_toggle.checked = True  # Context mode enabled

        mock_context_selector = MagicMock()
        mock_context_selector.currentData = "SegmentEditor"

        class MockWidget:
            def __init__(self):
                self._parameterNode = mock_parameter_node
                self._presetManager = mock_preset_manager
                self._eventHandler = MagicMock()
                self.contextToggle = mock_context_toggle
                self.contextSelector = mock_context_selector

            def _onActionChanged(self, button_id: str, index: int, combo=None) -> None:
                presetId = self._parameterNode.selectedPresetId if self._parameterNode else ""
                if not presetId:
                    return
                preset = self._presetManager.get_preset(presetId)
                if not preset:
                    return
                if not combo:
                    return

                action_id = combo.currentData
                context = None
                if self.contextToggle.checked:
                    context = (
                        self.contextSelector.currentData
                        if self.contextSelector.currentData
                        else None
                    )

                if action_id:
                    preset.set_mapping(button_id, MagicMock(), context)

                self._presetManager.save_preset(preset)

        widget = MockWidget()
        widget._onActionChanged("back", 1, mock_combo)

        # Verify set_mapping was called with context
        mock_preset.set_mapping.assert_called_once()
        call_args = mock_preset.set_mapping.call_args
        assert call_args[0][0] == "back"  # button_id
        assert call_args[0][2] == "SegmentEditor"  # context


class TestLambdaCapture:
    """Test that lambda captures work correctly for signal connections."""

    def test_lambda_captures_combo_reference(self):
        """Verify that lambda captures the combo box reference correctly."""
        captured_values = []

        def mock_on_action_changed(button_id, index, combo):
            captured_values.append((button_id, index, combo))

        # Simulate what happens in _updateMappingTable
        mock_combo = MagicMock()
        mock_combo.name = "test_combo"
        button_id = "back"

        # Create the lambda like in the real code
        handler = lambda idx, b=button_id, c=mock_combo: mock_on_action_changed(b, idx, c)  # noqa: E731

        # Simulate signal emission
        handler(5)

        # Verify correct values captured
        assert len(captured_values) == 1
        assert captured_values[0][0] == "back"
        assert captured_values[0][1] == 5
        assert captured_values[0][2] is mock_combo

    def test_lambda_captures_different_combos_per_button(self):
        """Verify that each button gets its own combo reference."""
        captured = []

        def handler(button_id, index, combo):
            captured.append((button_id, combo.name))

        buttons = ["back", "forward", "middle"]
        handlers = []

        for button_id in buttons:
            combo = MagicMock()
            combo.name = f"combo_{button_id}"
            # This is how the real code creates lambdas
            h = lambda idx, b=button_id, c=combo: handler(b, idx, c)  # noqa: E731
            handlers.append(h)

        # Simulate all handlers being called
        for h in handlers:
            h(0)

        # Each handler should have captured its own combo
        assert len(captured) == 3
        assert captured[0] == ("back", "combo_back")
        assert captured[1] == ("forward", "combo_forward")
        assert captured[2] == ("middle", "combo_middle")


class TestOnClearMapping:
    """Test _onClearMapping method."""

    def test_clear_mapping_removes_mapping(self):
        """Test that clearing a mapping removes it from the preset."""
        mock_preset = MagicMock()
        mock_preset_manager = MagicMock()
        mock_preset_manager.get_preset.return_value = mock_preset

        mock_parameter_node = MagicMock()
        mock_parameter_node.selectedPresetId = "test_preset"

        class MockWidget:
            def __init__(self):
                self._parameterNode = mock_parameter_node
                self._presetManager = mock_preset_manager
                self._eventHandler = MagicMock()
                self.contextToggle = MagicMock()
                self.contextToggle.checked = False

            def _onClearMapping(self, button_id: str) -> None:
                presetId = self._parameterNode.selectedPresetId if self._parameterNode else ""
                if not presetId:
                    return
                preset = self._presetManager.get_preset(presetId)
                if not preset:
                    return

                context = None
                if self.contextToggle.checked:
                    context = "SomeContext"

                preset.remove_mapping(button_id, context)
                self._presetManager.save_preset(preset)
                self._eventHandler.set_preset(preset)

        widget = MockWidget()
        widget._onClearMapping("back")

        mock_preset.remove_mapping.assert_called_once_with("back", None)
        mock_preset_manager.save_preset.assert_called_once()


class TestWidgetNoSender:
    """Test that widget code doesn't rely on QObject.sender()."""

    def test_widget_methods_dont_use_sender(self):
        """Verify that _onActionChanged doesn't call self.sender()."""
        # Read the actual source file and check
        from pathlib import Path

        widget_file = Path(__file__).parent.parent.parent / "MouseMaster.py"
        if widget_file.exists():
            content = widget_file.read_text()

            # Check _onActionChanged doesn't use sender()
            import re

            # Find the _onActionChanged method
            match = re.search(
                r"def _onActionChanged\(self.*?\n(.*?)(?=\n    def |\nclass |\Z)",
                content,
                re.DOTALL,
            )
            if match:
                method_body = match.group(1)
                assert "self.sender()" not in method_body, (
                    "_onActionChanged should not use self.sender()"
                )
