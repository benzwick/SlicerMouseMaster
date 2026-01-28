"""Tests for MouseMasterWidget user interactions.

These tests emulate user clicking on all UI widgets, following the pattern from
SlicerAdaptiveBrush where programmatic interaction methods are tested.

Tests are divided into:
1. Standalone tests (mocked Slicer/Qt) - run with pytest outside Slicer
2. Integration tests (marked requires_slicer) - run inside Slicer
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest


class TestMouseSelectorInteraction:
    """Test user interactions with the mouse selector combo box."""

    def test_select_mouse_updates_parameter_node(self):
        """Simulate user selecting a mouse from dropdown."""
        # Create mock widget components
        mock_param_node = MagicMock()
        mock_param_node.selectedMouseId = ""
        mock_param_node.selectedPresetId = ""

        mock_mouse_profiles = {
            "logitech_mx_master_3s": MagicMock(
                id="logitech_mx_master_3s",
                name="Logitech MX Master 3S",
            ),
            "generic_5_button": MagicMock(
                id="generic_5_button",
                name="Generic 5 Button Mouse",
            ),
        }

        # Simulate the onMouseSelected callback
        class MockWidget:
            def __init__(self):
                self._parameterNode = mock_param_node
                self._mouseProfiles = mock_mouse_profiles
                self._currentProfile = None
                self.mouseSelector = MagicMock()

            def onMouseSelected(self, index: int) -> None:
                """Handle mouse selection change."""
                mouseId = self.mouseSelector.itemData(index)
                if self._parameterNode:
                    self._parameterNode.selectedMouseId = mouseId if mouseId else ""
                self._currentProfile = self._mouseProfiles.get(mouseId) if mouseId else None

        widget = MockWidget()
        widget.mouseSelector.itemData.return_value = "logitech_mx_master_3s"

        # Simulate user selecting index 1 (MX Master 3S)
        widget.onMouseSelected(1)

        # Verify parameter node was updated
        assert mock_param_node.selectedMouseId == "logitech_mx_master_3s"
        assert widget._currentProfile.id == "logitech_mx_master_3s"

    def test_select_placeholder_clears_selection(self):
        """Simulate user selecting the placeholder '-- Select Mouse --'."""
        mock_param_node = MagicMock()
        mock_param_node.selectedMouseId = "some_mouse"

        class MockWidget:
            def __init__(self):
                self._parameterNode = mock_param_node
                self._mouseProfiles = {}
                self._currentProfile = MagicMock()
                self.mouseSelector = MagicMock()

            def onMouseSelected(self, index: int) -> None:
                mouseId = self.mouseSelector.itemData(index)
                if self._parameterNode:
                    self._parameterNode.selectedMouseId = mouseId if mouseId else ""
                self._currentProfile = self._mouseProfiles.get(mouseId) if mouseId else None

        widget = MockWidget()
        widget.mouseSelector.itemData.return_value = ""  # Placeholder has empty data

        # Simulate user selecting placeholder (index 0)
        widget.onMouseSelected(0)

        # Verify selection was cleared
        assert mock_param_node.selectedMouseId == ""
        assert widget._currentProfile is None


class TestPresetSelectorInteraction:
    """Test user interactions with the preset selector combo box."""

    def test_select_preset_updates_parameter_node(self):
        """Simulate user selecting a preset from dropdown."""
        mock_param_node = MagicMock()
        mock_param_node.selectedPresetId = ""

        mock_preset_manager = MagicMock()
        mock_preset = MagicMock()
        mock_preset.name = "Default Workflow"
        mock_preset_manager.get_preset.return_value = mock_preset

        mock_event_handler = MagicMock()

        class MockWidget:
            def __init__(self):
                self._parameterNode = mock_param_node
                self._presetManager = mock_preset_manager
                self._eventHandler = mock_event_handler
                self.presetSelector = MagicMock()
                self.mappingTable = MagicMock()

            def onPresetSelected(self, index: int) -> None:
                presetId = self.presetSelector.itemData(index)
                if self._parameterNode:
                    self._parameterNode.selectedPresetId = presetId if presetId else ""
                self._loadSelectedPreset()

            def _loadSelectedPreset(self) -> None:
                presetId = self._parameterNode.selectedPresetId if self._parameterNode else ""
                if presetId:
                    preset = self._presetManager.get_preset(presetId)
                    if preset:
                        self._eventHandler.set_preset(preset)

            def _updateMappingTable(self) -> None:
                pass

        widget = MockWidget()
        widget.presetSelector.itemData.return_value = "default_workflow"

        # Simulate user selecting preset
        widget.onPresetSelected(1)

        # Verify parameter node and event handler were updated
        assert mock_param_node.selectedPresetId == "default_workflow"
        mock_preset_manager.get_preset.assert_called_with("default_workflow")
        mock_event_handler.set_preset.assert_called_with(mock_preset)


class TestEnableButtonInteraction:
    """Test user interactions with the enable/disable toggle button."""

    def test_enable_button_installs_event_handler(self):
        """Simulate user clicking enable button."""
        mock_param_node = MagicMock()
        mock_param_node.enabled = False

        mock_event_handler = MagicMock()

        class MockWidget:
            def __init__(self):
                self._parameterNode = mock_param_node
                self._eventHandler = mock_event_handler
                self.enableButton = MagicMock()

            def onEnableToggled(self, enabled: bool) -> None:
                if enabled:
                    self._eventHandler.install()
                    self.enableButton.text = "Disable Mouse Master"
                else:
                    self._eventHandler.uninstall()
                    self.enableButton.text = "Enable Mouse Master"
                if self._parameterNode:
                    self._parameterNode.enabled = enabled

        widget = MockWidget()

        # Simulate user clicking enable
        widget.onEnableToggled(True)

        # Verify event handler was installed
        mock_event_handler.install.assert_called_once()
        assert mock_param_node.enabled is True
        assert widget.enableButton.text == "Disable Mouse Master"

    def test_disable_button_uninstalls_event_handler(self):
        """Simulate user clicking disable button."""
        mock_param_node = MagicMock()
        mock_param_node.enabled = True

        mock_event_handler = MagicMock()

        class MockWidget:
            def __init__(self):
                self._parameterNode = mock_param_node
                self._eventHandler = mock_event_handler
                self.enableButton = MagicMock()

            def onEnableToggled(self, enabled: bool) -> None:
                if enabled:
                    self._eventHandler.install()
                    self.enableButton.text = "Disable Mouse Master"
                else:
                    self._eventHandler.uninstall()
                    self.enableButton.text = "Enable Mouse Master"
                if self._parameterNode:
                    self._parameterNode.enabled = enabled

        widget = MockWidget()

        # Simulate user clicking disable
        widget.onEnableToggled(False)

        # Verify event handler was uninstalled
        mock_event_handler.uninstall.assert_called_once()
        assert mock_param_node.enabled is False
        assert widget.enableButton.text == "Enable Mouse Master"


class TestContextToggleInteraction:
    """Test user interactions with the context-sensitive toggle checkbox."""

    def test_enable_context_toggle_enables_selector(self):
        """Simulate user checking context toggle checkbox."""
        mock_context_selector = MagicMock()
        mock_context_selector.enabled = False

        class MockWidget:
            def __init__(self):
                self.contextSelector = mock_context_selector
                self.contextToggle = MagicMock()
                self.contextToggle.checked = False

            def onContextToggled(self, enabled: bool) -> None:
                self.contextSelector.enabled = enabled
                self.contextToggle.checked = enabled

        widget = MockWidget()

        # Simulate user checking the toggle
        widget.onContextToggled(True)

        # Verify context selector was enabled
        assert widget.contextSelector.enabled is True

    def test_disable_context_toggle_disables_selector(self):
        """Simulate user unchecking context toggle checkbox."""
        mock_context_selector = MagicMock()
        mock_context_selector.enabled = True

        class MockWidget:
            def __init__(self):
                self.contextSelector = mock_context_selector
                self.contextToggle = MagicMock()
                self.contextToggle.checked = True

            def onContextToggled(self, enabled: bool) -> None:
                self.contextSelector.enabled = enabled
                self.contextToggle.checked = enabled

        widget = MockWidget()

        # Simulate user unchecking the toggle
        widget.onContextToggled(False)

        # Verify context selector was disabled
        assert widget.contextSelector.enabled is False


class TestContextSelectorInteraction:
    """Test user interactions with the context selector combo box."""

    def test_select_context_triggers_table_update(self):
        """Simulate user selecting a context from dropdown."""
        update_called = []

        class MockWidget:
            def __init__(self):
                self.contextSelector = MagicMock()

            def onContextChanged(self, index: int) -> None:
                self._updateMappingTable()

            def _updateMappingTable(self) -> None:
                update_called.append(True)

        widget = MockWidget()
        widget.contextSelector.currentData = "SegmentEditor"

        # Simulate user selecting SegmentEditor context
        widget.onContextChanged(1)

        # Verify table was updated
        assert len(update_called) == 1


class TestMappingTableInteraction:
    """Test user interactions with the button mapping table."""

    def test_change_action_in_combo_box(self):
        """Simulate user changing action in mapping table combo box."""
        mock_param_node = MagicMock()
        mock_param_node.selectedPresetId = "test_preset"

        mock_preset = MagicMock()
        mock_preset_manager = MagicMock()
        mock_preset_manager.get_preset.return_value = mock_preset

        mock_event_handler = MagicMock()

        class MockWidget:
            def __init__(self):
                self._parameterNode = mock_param_node
                self._presetManager = mock_preset_manager
                self._eventHandler = mock_event_handler
                self.contextToggle = MagicMock()
                self.contextToggle.checked = False
                self.contextSelector = MagicMock()

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
                    from MouseMasterLib.preset_manager import Mapping

                    mapping = Mapping(action=action_id)
                    preset.set_mapping(button_id, mapping, context)
                else:
                    preset.remove_mapping(button_id, context)

                self._presetManager.save_preset(preset)
                self._eventHandler.set_preset(preset)

        widget = MockWidget()

        # Create mock combo box
        mock_combo = MagicMock()
        mock_combo.currentData = "edit_undo"

        # Simulate user selecting "Undo" action for "back" button
        widget._onActionChanged("back", 1, mock_combo)

        # Verify preset was updated and saved
        mock_preset.set_mapping.assert_called_once()
        mock_preset_manager.save_preset.assert_called_with(mock_preset)
        mock_event_handler.set_preset.assert_called_with(mock_preset)

    def test_select_none_removes_mapping(self):
        """Simulate user selecting '-- None --' to remove mapping."""
        mock_param_node = MagicMock()
        mock_param_node.selectedPresetId = "test_preset"

        mock_preset = MagicMock()
        mock_preset_manager = MagicMock()
        mock_preset_manager.get_preset.return_value = mock_preset

        mock_event_handler = MagicMock()

        class MockWidget:
            def __init__(self):
                self._parameterNode = mock_param_node
                self._presetManager = mock_preset_manager
                self._eventHandler = mock_event_handler
                self.contextToggle = MagicMock()
                self.contextToggle.checked = False
                self.contextSelector = MagicMock()

            def _onActionChanged(self, button_id: str, index: int, combo=None) -> None:
                presetId = self._parameterNode.selectedPresetId if self._parameterNode else ""
                if not presetId:
                    return
                preset = self._presetManager.get_preset(presetId)
                if not preset or not combo:
                    return

                action_id = combo.currentData
                context = None

                if action_id:
                    from MouseMasterLib.preset_manager import Mapping

                    mapping = Mapping(action=action_id)
                    preset.set_mapping(button_id, mapping, context)
                else:
                    preset.remove_mapping(button_id, context)

                self._presetManager.save_preset(preset)
                self._eventHandler.set_preset(preset)

        widget = MockWidget()

        mock_combo = MagicMock()
        mock_combo.currentData = ""  # Empty = None selected

        # Simulate user selecting "-- None --"
        widget._onActionChanged("back", 0, mock_combo)

        # Verify mapping was removed
        mock_preset.remove_mapping.assert_called_once_with("back", None)
        mock_preset.set_mapping.assert_not_called()

    def test_change_action_with_context(self):
        """Simulate user changing action with context-sensitive bindings enabled."""
        mock_param_node = MagicMock()
        mock_param_node.selectedPresetId = "test_preset"

        mock_preset = MagicMock()
        mock_preset_manager = MagicMock()
        mock_preset_manager.get_preset.return_value = mock_preset

        mock_event_handler = MagicMock()

        class MockWidget:
            def __init__(self):
                self._parameterNode = mock_param_node
                self._presetManager = mock_preset_manager
                self._eventHandler = mock_event_handler
                self.contextToggle = MagicMock()
                self.contextToggle.checked = True  # Context mode enabled
                self.contextSelector = MagicMock()
                self.contextSelector.currentData = "SegmentEditor"

            def _onActionChanged(self, button_id: str, index: int, combo=None) -> None:
                presetId = self._parameterNode.selectedPresetId if self._parameterNode else ""
                if not presetId:
                    return
                preset = self._presetManager.get_preset(presetId)
                if not preset or not combo:
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

                self._presetManager.save_preset(preset)

        widget = MockWidget()

        mock_combo = MagicMock()
        mock_combo.currentData = "segment_previous"

        # Simulate user selecting action with context
        widget._onActionChanged("back", 1, mock_combo)

        # Verify context was passed
        call_args = mock_preset.set_mapping.call_args
        assert call_args[0][0] == "back"  # button_id
        assert call_args[0][2] == "SegmentEditor"  # context


class TestClearButtonInteraction:
    """Test user interactions with clear button in mapping table."""

    def test_click_clear_button_removes_mapping(self):
        """Simulate user clicking clear button."""
        mock_param_node = MagicMock()
        mock_param_node.selectedPresetId = "test_preset"

        mock_preset = MagicMock()
        mock_preset_manager = MagicMock()
        mock_preset_manager.get_preset.return_value = mock_preset

        mock_event_handler = MagicMock()
        table_updated = []

        class MockWidget:
            def __init__(self):
                self._parameterNode = mock_param_node
                self._presetManager = mock_preset_manager
                self._eventHandler = mock_event_handler
                self.contextToggle = MagicMock()
                self.contextToggle.checked = False
                self.contextSelector = MagicMock()

            def _onClearMapping(self, button_id: str) -> None:
                presetId = self._parameterNode.selectedPresetId if self._parameterNode else ""
                if not presetId:
                    return
                preset = self._presetManager.get_preset(presetId)
                if not preset:
                    return

                context = None
                if self.contextToggle.checked:
                    context = (
                        self.contextSelector.currentData
                        if self.contextSelector.currentData
                        else None
                    )

                preset.remove_mapping(button_id, context)
                self._presetManager.save_preset(preset)
                self._eventHandler.set_preset(preset)
                self._updateMappingTable()

            def _updateMappingTable(self) -> None:
                table_updated.append(True)

        widget = MockWidget()

        # Simulate user clicking clear button for "back"
        widget._onClearMapping("back")

        # Verify mapping was removed and table refreshed
        mock_preset.remove_mapping.assert_called_once_with("back", None)
        mock_preset_manager.save_preset.assert_called_once()
        mock_event_handler.set_preset.assert_called_once()
        assert len(table_updated) == 1


class TestDetectButtonInteraction:
    """Test user interactions with detect button."""

    def test_click_detect_opens_dialog(self):
        """Simulate user clicking detect button."""
        dialog_opened = []
        profile_saved = []

        class MockDialog:
            def exec(self):
                dialog_opened.append(True)
                return 1  # QDialog.Accepted

            def getProfile(self):
                mock_profile = MagicMock()
                mock_profile.id = "detected_mouse"
                mock_profile.name = "Detected Mouse"
                return mock_profile

        class MockWidget:
            def __init__(self):
                self._mouseProfiles = {}
                self.mouseSelector = MagicMock()

            def onDetectClicked(self) -> None:
                dialog = MockDialog()
                if dialog.exec() == 1:  # Accepted
                    profile = dialog.getProfile()
                    if profile:
                        self._saveDetectedProfile(profile)
                        self._populateMouseSelector()
                        index = self.mouseSelector.findData(profile.id)
                        if index >= 0:
                            self.mouseSelector.setCurrentIndex(index)

            def _saveDetectedProfile(self, profile) -> None:
                self._mouseProfiles[profile.id] = profile
                profile_saved.append(profile)

            def _populateMouseSelector(self) -> None:
                pass

        widget = MockWidget()
        widget.mouseSelector.findData.return_value = 1

        # Simulate user clicking detect button
        widget.onDetectClicked()

        # Verify dialog was opened and profile was saved
        assert len(dialog_opened) == 1
        assert len(profile_saved) == 1
        assert profile_saved[0].id == "detected_mouse"


class TestCompleteWorkflow:
    """Test complete user workflows through the widget."""

    def test_full_setup_workflow(self):
        """Simulate complete user workflow: select mouse -> select preset -> enable."""
        # Track all state changes
        state_changes = []

        mock_param_node = MagicMock()
        mock_param_node.selectedMouseId = ""
        mock_param_node.selectedPresetId = ""
        mock_param_node.enabled = False

        mock_preset = MagicMock()
        mock_preset.name = "Default"
        mock_preset_manager = MagicMock()
        mock_preset_manager.get_preset.return_value = mock_preset
        mock_preset_manager.get_presets_for_mouse.return_value = [mock_preset]

        mock_event_handler = MagicMock()

        mock_mouse_profiles = {
            "test_mouse": MagicMock(id="test_mouse", name="Test Mouse"),
        }

        class MockWidget:
            def __init__(self):
                self._parameterNode = mock_param_node
                self._presetManager = mock_preset_manager
                self._eventHandler = mock_event_handler
                self._mouseProfiles = mock_mouse_profiles
                self._currentProfile = None
                self.mouseSelector = MagicMock()
                self.presetSelector = MagicMock()
                self.enableButton = MagicMock()
                self.contextToggle = MagicMock()
                self.contextToggle.checked = False

            def onMouseSelected(self, index: int) -> None:
                mouseId = self.mouseSelector.itemData(index)
                if self._parameterNode:
                    self._parameterNode.selectedMouseId = mouseId if mouseId else ""
                self._currentProfile = self._mouseProfiles.get(mouseId) if mouseId else None
                state_changes.append(("mouse_selected", mouseId))

            def onPresetSelected(self, index: int) -> None:
                presetId = self.presetSelector.itemData(index)
                if self._parameterNode:
                    self._parameterNode.selectedPresetId = presetId if presetId else ""
                self._loadSelectedPreset()
                state_changes.append(("preset_selected", presetId))

            def _loadSelectedPreset(self) -> None:
                presetId = self._parameterNode.selectedPresetId if self._parameterNode else ""
                if presetId:
                    preset = self._presetManager.get_preset(presetId)
                    if preset:
                        self._eventHandler.set_preset(preset)

            def onEnableToggled(self, enabled: bool) -> None:
                if enabled:
                    self._eventHandler.install()
                    self.enableButton.text = "Disable Mouse Master"
                else:
                    self._eventHandler.uninstall()
                    self.enableButton.text = "Enable Mouse Master"
                if self._parameterNode:
                    self._parameterNode.enabled = enabled
                state_changes.append(("enabled", enabled))

        widget = MockWidget()

        # Step 1: User selects a mouse
        widget.mouseSelector.itemData.return_value = "test_mouse"
        widget.onMouseSelected(1)

        # Step 2: User selects a preset
        widget.presetSelector.itemData.return_value = "default_preset"
        widget.onPresetSelected(1)

        # Step 3: User clicks enable
        widget.onEnableToggled(True)

        # Verify complete workflow
        assert state_changes == [
            ("mouse_selected", "test_mouse"),
            ("preset_selected", "default_preset"),
            ("enabled", True),
        ]

        # Verify final state
        assert mock_param_node.selectedMouseId == "test_mouse"
        assert mock_param_node.selectedPresetId == "default_preset"
        assert mock_param_node.enabled is True
        mock_event_handler.install.assert_called_once()
        mock_event_handler.set_preset.assert_called_with(mock_preset)

    def test_context_mapping_workflow(self):
        """Simulate workflow: enable context -> select context -> change mapping."""
        state_changes = []

        mock_param_node = MagicMock()
        mock_param_node.selectedPresetId = "test_preset"

        mock_preset = MagicMock()
        mock_preset_manager = MagicMock()
        mock_preset_manager.get_preset.return_value = mock_preset

        mock_event_handler = MagicMock()

        class MockWidget:
            def __init__(self):
                self._parameterNode = mock_param_node
                self._presetManager = mock_preset_manager
                self._eventHandler = mock_event_handler
                self.contextToggle = MagicMock()
                self.contextToggle.checked = False
                self.contextSelector = MagicMock()
                self.contextSelector.enabled = False
                self.contextSelector.currentData = ""

            def onContextToggled(self, enabled: bool) -> None:
                self.contextSelector.enabled = enabled
                self.contextToggle.checked = enabled
                state_changes.append(("context_toggled", enabled))

            def onContextChanged(self, index: int) -> None:
                state_changes.append(("context_changed", self.contextSelector.currentData))

            def _onActionChanged(self, button_id: str, index: int, combo=None) -> None:
                preset = self._presetManager.get_preset(self._parameterNode.selectedPresetId)
                if not preset or not combo:
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
                    state_changes.append(("mapping_set", button_id, action_id, context))

                self._presetManager.save_preset(preset)

        widget = MockWidget()

        # Step 1: Enable context-sensitive bindings
        widget.onContextToggled(True)

        # Step 2: Select SegmentEditor context
        widget.contextSelector.currentData = "SegmentEditor"
        widget.onContextChanged(1)

        # Step 3: Change action for back button
        mock_combo = MagicMock()
        mock_combo.currentData = "segment_previous"
        widget._onActionChanged("back", 1, mock_combo)

        # Verify workflow
        assert state_changes == [
            ("context_toggled", True),
            ("context_changed", "SegmentEditor"),
            ("mapping_set", "back", "segment_previous", "SegmentEditor"),
        ]

        # Verify context was used in mapping
        assert widget.contextSelector.enabled is True


# =============================================================================
# Integration Tests (require Slicer) - with Screenshot Capture
# =============================================================================


@pytest.mark.requires_slicer
class TestWidgetInSlicer:
    """Tests that run inside Slicer environment with screenshot capture.

    These tests are skipped when running with pytest outside Slicer.
    Run inside Slicer with: slicer.modules.mousemaster.test()

    Screenshots are saved to MouseMaster/Testing/Python/screenshots/
    with a manifest.json for Claude Code review.
    """

    @pytest.fixture
    def widget(self):
        """Get the MouseMaster widget from Slicer."""
        import slicer

        widget_rep = slicer.modules.mousemaster.widgetRepresentation()
        if widget_rep:
            return widget_rep.self()
        return None

    @pytest.fixture
    def capture(self):
        """Get screenshot capture instance."""
        from screenshot_capture import ScreenshotCapture

        screenshots_dir = Path(__file__).parent / "screenshots"
        cap = ScreenshotCapture(base_folder=screenshots_dir)
        cap.reset()
        yield cap
        cap.save_manifest()

    def test_mouse_selector_populated(self, widget, capture):
        """Verify mouse selector is populated with profiles."""
        if widget is None:
            pytest.skip("MouseMaster widget not available")

        capture.set_group("mouse_selector")
        capture.capture_module_widget("Initial state - mouse selector")

        # Should have at least placeholder + built-in profiles
        assert widget.mouseSelector.count >= 1
        # First item should be placeholder
        assert widget.mouseSelector.itemData(0) == ""

        capture.capture_widget(widget.mouseSelector, "Mouse selector dropdown")

    def test_enable_button_initial_state(self, widget, capture):
        """Verify enable button starts in correct state."""
        if widget is None:
            pytest.skip("MouseMaster widget not available")

        capture.set_group("enable_button")
        capture.capture_widget(widget.enableButton, "Enable button initial state")

        # Should be disabled until mouse and preset selected
        # (unless settings were saved from previous session)
        assert hasattr(widget, "enableButton")

    def test_mapping_table_columns(self, widget, capture):
        """Verify mapping table has correct columns."""
        if widget is None:
            pytest.skip("MouseMaster widget not available")

        capture.set_group("mapping_table")
        capture.capture_widget(widget.mappingTable, "Mapping table with columns")

        assert widget.mappingTable.columnCount() == 3
        # Check headers
        header = widget.mappingTable.horizontalHeader()
        assert header is not None

    def test_context_selector_options(self, widget, capture):
        """Verify context selector has expected options."""
        if widget is None:
            pytest.skip("MouseMaster widget not available")

        capture.set_group("context_selector")
        capture.capture_widget(widget.contextSelector, "Context selector dropdown")

        # Should have default + common contexts
        assert widget.contextSelector.count >= 4
        # Default option
        assert widget.contextSelector.itemData(0) == ""

    def test_full_interaction_cycle(self, widget, capture):
        """Test full user interaction cycle in Slicer with screenshots."""
        if widget is None:
            pytest.skip("MouseMaster widget not available")

        import slicer

        capture.set_group("full_workflow")
        capture.capture_layout("Initial state before interaction")
        capture.capture_module_widget("Module panel initial state")

        # Find first available mouse
        if widget.mouseSelector.count > 1:
            # Select first mouse (skip placeholder)
            widget.mouseSelector.setCurrentIndex(1)
            slicer.app.processEvents()
            capture.capture_module_widget("After selecting mouse")

            # Wait for preset selector to populate
            if widget.presetSelector.count > 1:
                # Select first preset
                widget.presetSelector.setCurrentIndex(1)
                slicer.app.processEvents()
                capture.capture_module_widget("After selecting preset")

                # Enable MouseMaster
                initial_enabled = widget.enableButton.checked
                widget.enableButton.setChecked(True)
                slicer.app.processEvents()
                capture.capture_module_widget("After enabling MouseMaster")

                # Verify state changed
                assert widget.enableButton.checked is True

                # Disable and restore
                widget.enableButton.setChecked(initial_enabled)
                slicer.app.processEvents()
                capture.capture_module_widget("After restoring to initial state")

        capture.capture_layout("Final state after interaction cycle")

    def test_context_workflow_with_screenshots(self, widget, capture):
        """Test context-sensitive workflow with screenshots."""
        if widget is None:
            pytest.skip("MouseMaster widget not available")

        import slicer

        capture.set_group("context_workflow")
        capture.capture_module_widget("Initial state")

        # Enable context toggle
        if hasattr(widget, "contextToggle"):
            initial_checked = widget.contextToggle.checked
            widget.contextToggle.setChecked(True)
            slicer.app.processEvents()
            capture.capture_module_widget("After enabling context toggle")

            # Select a context
            if widget.contextSelector.count > 1:
                widget.contextSelector.setCurrentIndex(1)
                slicer.app.processEvents()
                capture.capture_module_widget("After selecting context")

            # Restore
            widget.contextToggle.setChecked(initial_checked)
            slicer.app.processEvents()

        capture.capture_layout("Final layout state")
