import logging
from pathlib import Path

import ctk
import slicer
import vtk
from slicer.i18n import tr as _
from slicer.i18n import translate
from slicer.parameterNodeWrapper import parameterNodeWrapper
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

# MouseMaster library imports
from MouseMasterLib import MouseMasterEventHandler, PresetManager
from MouseMasterLib.action_registry import ActionRegistry
from MouseMasterLib.button_detector import ButtonDetector
from MouseMasterLib.mouse_profile import MouseProfile
from MouseMasterLib.preset_manager import Mapping

#
# MouseMaster
#


class MouseMaster(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    # Class-level event handler shared across module instances
    _sharedEventHandler: MouseMasterEventHandler | None = None

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = _("Mouse Master")
        # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.categories = [translate("qSlicerAbstractCoreModule", "Utilities")]
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["SlicerMouseMaster Contributors"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        # _() function marks text as translatable to other languages
        self.parent.helpText = _("""
Mouse customization extension for 3D Slicer. Provides button remapping,
workflow presets, and context-sensitive bindings for multi-button mice.
See more information in <a href="https://github.com/benzwick/SlicerMouseMaster#readme">module documentation</a>.
""")
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = _("""
This extension was developed by the SlicerMouseMaster contributors.
Based on the Slicer extension template.
""")
        # Schedule startup initialization after Slicer is fully loaded
        import qt
        qt.QTimer.singleShot(0, self._onStartupComplete)

    def _onStartupComplete(self) -> None:
        """Called after Slicer startup to initialize event handler if enabled."""
        import qt
        # Wait a bit more for layout to be ready
        qt.QTimer.singleShot(1000, self._initializeEventHandler)

    def _initializeEventHandler(self) -> None:
        """Initialize event handler at startup if previously enabled."""
        # Load settings to check if MouseMaster was enabled
        settings = slicer.app.settings()
        enabled = settings.value("MouseMaster/enabled", False)
        # QSettings may return string or bool depending on backend
        if isinstance(enabled, str):
            enabled = enabled.lower() == "true"
        mouseId = settings.value("MouseMaster/selectedMouseId", "")
        presetId = settings.value("MouseMaster/selectedPresetId", "")

        if not enabled or not mouseId or not presetId:
            logging.debug("[MouseMaster] Startup: not enabled or no mouse/preset selected")
            return

        logging.info(f"[MouseMaster] Startup: auto-enabling with mouse={mouseId}, preset={presetId}")

        # Create shared event handler if needed
        if MouseMaster._sharedEventHandler is None:
            MouseMaster._sharedEventHandler = MouseMasterEventHandler()

        # Load and set the preset
        builtin_presets_dir = Path(__file__).parent / "presets" / "builtin"
        if not builtin_presets_dir.exists():
            builtin_presets_dir = Path(__file__).parent.parent / "presets" / "builtin"

        user_presets_dir = Path(slicer.app.settings().fileName()).parent / "MouseMaster" / "presets"

        presetManager = PresetManager(
            builtin_dir=builtin_presets_dir,
            user_dir=user_presets_dir,
        )
        presetManager.load_all()

        preset = presetManager.get_preset(presetId)
        if preset:
            MouseMaster._sharedEventHandler.set_preset(preset)
            MouseMaster._sharedEventHandler.install()
            logging.info(f"[MouseMaster] Startup: event handler installed with preset '{preset.name}'")





#
# MouseMasterParameterNode
#


@parameterNodeWrapper
class MouseMasterParameterNode:
    """
    The parameters needed by module.

    enabled - Whether mouse button interception is active.
    selectedMouseId - ID of the selected mouse profile.
    selectedPresetId - ID of the selected button mapping preset.
    """

    enabled: bool = False
    selectedMouseId: str = ""
    selectedPresetId: str = ""


#
# MouseMasterWidget
#


class MouseMasterWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        # MouseMaster specific
        self._eventHandler = None
        self._presetManager = None
        self._currentProfile: MouseProfile | None = None
        self._actionRegistry = ActionRegistry.get_instance()
        self._mouseProfiles: dict[str, MouseProfile] = {}

    def setup(self) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.setup(self)

        # Create programmatic UI for MouseMaster
        self._setupUI()

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = MouseMasterLogic()

        # Initialize MouseMaster components - use shared handler if available
        if MouseMaster._sharedEventHandler is not None:
            self._eventHandler = MouseMaster._sharedEventHandler
        else:
            self._eventHandler = MouseMasterEventHandler()
            MouseMaster._sharedEventHandler = self._eventHandler
        # Presets are in presets/builtin/ at project root (one level up from MouseMaster/)
        module_dir = Path(__file__).parent
        project_dir = module_dir.parent
        self._presetManager = PresetManager(
            builtin_dir=project_dir / "presets" / "builtin",
            user_dir=Path(slicer.app.slicerUserSettingsFilePath).parent / "MouseMaster" / "presets",
        )
        # Load mouse profiles from MouseDefinitions
        self._loadMouseProfiles()

        # Discover Slicer menu actions
        self._actionRegistry.discover_slicer_actions()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def _setupUI(self) -> None:
        """Create the MouseMaster user interface programmatically."""
        import qt

        # Collapsible button for mouse selection
        mouseCollapsible = ctk.ctkCollapsibleButton()
        mouseCollapsible.text = "Mouse Selection"
        self.layout.addWidget(mouseCollapsible)
        mouseLayout = qt.QFormLayout(mouseCollapsible)

        # Mouse selector combo box
        self.mouseSelector = qt.QComboBox()
        self.mouseSelector.addItem("-- Select Mouse --", "")
        mouseLayout.addRow("Mouse Model:", self.mouseSelector)

        # Detect button
        self.detectButton = qt.QPushButton("Detect New Mouse...")
        self.detectButton.toolTip = "Detect button codes for an unlisted mouse"
        mouseLayout.addRow(self.detectButton)

        # Collapsible button for preset management
        presetCollapsible = ctk.ctkCollapsibleButton()
        presetCollapsible.text = "Preset Management"
        self.layout.addWidget(presetCollapsible)
        presetLayout = qt.QFormLayout(presetCollapsible)

        # Preset selector combo box
        self.presetSelector = qt.QComboBox()
        self.presetSelector.addItem("-- Select Preset --", "")
        presetLayout.addRow("Preset:", self.presetSelector)

        # Enable/Disable button
        self.enableButton = qt.QPushButton("Enable Mouse Master")
        self.enableButton.checkable = True
        self.enableButton.checked = False
        presetLayout.addRow(self.enableButton)

        # Collapsible button for button mappings
        mappingsCollapsible = ctk.ctkCollapsibleButton()
        mappingsCollapsible.text = "Button Mappings"
        mappingsCollapsible.collapsed = True
        self.layout.addWidget(mappingsCollapsible)
        mappingsLayout = qt.QVBoxLayout(mappingsCollapsible)

        # Context-sensitive toggle
        self.contextToggle = qt.QCheckBox("Enable context-sensitive bindings")
        self.contextToggle.toolTip = "Use different bindings for different Slicer modules"
        mappingsLayout.addWidget(self.contextToggle)

        # Context selector (only visible when context toggle is enabled)
        contextRow = qt.QHBoxLayout()
        contextLabel = qt.QLabel("Context:")
        self.contextSelector = qt.QComboBox()
        self.contextSelector.addItem("Default (all modules)", "")
        self.contextSelector.addItem("Segment Editor", "SegmentEditor")
        self.contextSelector.addItem("Markups", "Markups")
        self.contextSelector.addItem("Volume Rendering", "VolumeRendering")
        self.contextSelector.enabled = False
        contextRow.addWidget(contextLabel)
        contextRow.addWidget(self.contextSelector)
        contextRow.addStretch()
        mappingsLayout.addLayout(contextRow)

        # Button mapping table
        self.mappingTable = qt.QTableWidget()
        self.mappingTable.setColumnCount(3)
        self.mappingTable.setHorizontalHeaderLabels(["Button", "Action", ""])
        self.mappingTable.horizontalHeader().setStretchLastSection(False)
        self.mappingTable.horizontalHeader().setSectionResizeMode(0, qt.QHeaderView.ResizeToContents)
        self.mappingTable.horizontalHeader().setSectionResizeMode(1, qt.QHeaderView.Stretch)
        self.mappingTable.horizontalHeader().setSectionResizeMode(2, qt.QHeaderView.ResizeToContents)
        self.mappingTable.setSelectionBehavior(qt.QAbstractItemView.SelectRows)
        self.mappingTable.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
        self.mappingTable.setMinimumHeight(250)
        mappingsLayout.addWidget(self.mappingTable)

        # Connect signals
        self.enableButton.connect("toggled(bool)", self.onEnableToggled)
        self.mouseSelector.connect("currentIndexChanged(int)", self.onMouseSelected)
        self.presetSelector.connect("currentIndexChanged(int)", self.onPresetSelected)
        self.contextToggle.connect("toggled(bool)", self.onContextToggled)
        self.contextSelector.connect("currentIndexChanged(int)", self.onContextChanged)
        self.detectButton.connect("clicked()", self.onDetectClicked)

        # Add stretch to push widgets to top
        self.layout.addStretch(1)

    def cleanup(self) -> None:
        """Called when the application closes and the module widget is destroyed."""
        # Save settings to application settings for persistence across sessions
        self._saveApplicationSettings()
        self.removeObservers()
        # Note: Don't uninstall the shared event handler here - it should persist
        # across module changes. It will be uninstalled when the user disables it
        # or when Slicer exits.

    def enter(self) -> None:
        """Called each time the user opens this module."""
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self) -> None:
        """Called each time the user opens a different module."""
        # Do not react to parameter node changes (GUI will be updated when the user enters into the module)
        if self._parameterNode:
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)

    def onSceneStartClose(self, caller, event) -> None:
        """Called just before the scene is closed."""
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event) -> None:
        """Called just after the scene is closed."""
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self) -> None:
        """Ensure parameter node exists and observed."""
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Load settings from application settings if parameter node is empty
        # (happens on fresh Slicer start without a saved scene)
        if not self._parameterNode.selectedMouseId:
            self._loadApplicationSettings()

        # Block signals while populating and restoring UI to prevent
        # combo box changes from overwriting saved parameter node values
        self.mouseSelector.blockSignals(True)
        self.presetSelector.blockSignals(True)
        self.enableButton.blockSignals(True)

        self._populateMouseSelector()
        self._restoreUIState()

        self.mouseSelector.blockSignals(False)
        self.presetSelector.blockSignals(False)
        self.enableButton.blockSignals(False)

    def setParameterNode(self, inputParameterNode: MouseMasterParameterNode | None) -> None:
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if self._parameterNode:
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
        self._parameterNode = inputParameterNode
        if self._parameterNode:
            # Note: We use programmatic UI, not .ui file with automatic parameter binding
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
            self._checkCanApply()

    def _checkCanApply(self, caller=None, event=None) -> None:
        """Check if MouseMaster can be enabled (mouse and preset selected)."""
        canEnable = bool(self._parameterNode and
                        self._parameterNode.selectedMouseId and
                        self._parameterNode.selectedPresetId)
        self.enableButton.enabled = canEnable
        if not canEnable:
            self.enableButton.toolTip = _("Select a mouse and preset first")
        else:
            self.enableButton.toolTip = _("Enable/disable mouse button interception")

    def _populateMouseSelector(self) -> None:
        """Populate the mouse selector with available profiles."""
        self.mouseSelector.clear()
        self.mouseSelector.addItem("-- Select Mouse --", "")
        # Add loaded mouse profiles
        for profile_id, profile in self._mouseProfiles.items():
            self.mouseSelector.addItem(profile.name, profile_id)

    def _restoreUIState(self) -> None:
        """Restore UI state from parameter node."""
        if not self._parameterNode:
            return

        # Restore mouse selection
        mouseId = self._parameterNode.selectedMouseId
        logging.info(f"[MouseMaster] Restoring UI - mouseId: {mouseId!r}")
        if mouseId:
            index = self.mouseSelector.findData(mouseId)
            logging.info(f"[MouseMaster] Mouse index found: {index}")
            if index >= 0:
                self.mouseSelector.setCurrentIndex(index)

        # Restore preset selection (this also loads the preset)
        self._updatePresetSelector()
        presetId = self._parameterNode.selectedPresetId
        logging.info(f"[MouseMaster] Restoring UI - presetId: {presetId!r}")
        if presetId:
            index = self.presetSelector.findData(presetId)
            logging.info(f"[MouseMaster] Preset index found: {index}")
            if index >= 0:
                self.presetSelector.setCurrentIndex(index)
            self._loadSelectedPreset()

        # Restore enabled state
        logging.info(f"[MouseMaster] Restoring UI - enabled: {self._parameterNode.enabled}")
        if self._parameterNode.enabled:
            self.enableButton.setChecked(True)
            # Must explicitly call handler since signals are blocked during restore
            self.onEnableToggled(True)

    def onEnableToggled(self, enabled: bool) -> None:
        """Handle enable/disable toggle."""
        if enabled:
            self._eventHandler.install()
            self.enableButton.text = "Disable Mouse Master"
            logging.info("MouseMaster enabled")
        else:
            self._eventHandler.uninstall()
            self.enableButton.text = "Enable Mouse Master"
            logging.info("MouseMaster disabled")
        if self._parameterNode:
            self._parameterNode.enabled = enabled

    def onMouseSelected(self, index: int) -> None:
        """Handle mouse selection change."""
        mouseId = self.mouseSelector.itemData(index)
        if self._parameterNode:
            self._parameterNode.selectedMouseId = mouseId if mouseId else ""
        # Update current profile
        self._currentProfile = self._mouseProfiles.get(mouseId) if mouseId else None
        self._updatePresetSelector()
        self._updateMappingTable()

    def onPresetSelected(self, index: int) -> None:
        """Handle preset selection change."""
        presetId = self.presetSelector.itemData(index)
        if self._parameterNode:
            self._parameterNode.selectedPresetId = presetId if presetId else ""
        self._loadSelectedPreset()

    def _updatePresetSelector(self) -> None:
        """Update preset selector based on selected mouse."""
        self.presetSelector.clear()
        self.presetSelector.addItem("-- Select Preset --", "")
        mouseId = self._parameterNode.selectedMouseId if self._parameterNode else ""
        if mouseId:
            presets = self._presetManager.get_presets_for_mouse(mouseId)
            for preset in presets:
                self.presetSelector.addItem(preset.name, preset.id)

    def _loadSelectedPreset(self) -> None:
        """Load the selected preset into the event handler."""
        presetId = self._parameterNode.selectedPresetId if self._parameterNode else ""
        if presetId:
            preset = self._presetManager.get_preset(presetId)
            if preset:
                self._eventHandler.set_preset(preset)
                logging.info(f"Loaded preset: {preset.name}")
                self._updateMappingTable()

    def _loadMouseProfiles(self) -> None:
        """Load mouse profiles from the MouseDefinitions directories."""
        # Load built-in profiles
        module_dir = Path(__file__).parent
        definitions_dir = module_dir / "Resources" / "MouseDefinitions"
        if definitions_dir.exists():
            for json_file in definitions_dir.glob("*.json"):
                profile = MouseProfile.from_json_file(json_file)
                self._mouseProfiles[profile.id] = profile
                logging.info(f"Loaded built-in mouse profile: {profile.name}")

        # Load user profiles (can override built-in)
        user_dir = Path(slicer.app.slicerUserSettingsFilePath).parent / "MouseMaster" / "MouseDefinitions"
        if user_dir.exists():
            for json_file in user_dir.glob("*.json"):
                profile = MouseProfile.from_json_file(json_file)
                self._mouseProfiles[profile.id] = profile
                logging.info(f"Loaded user mouse profile: {profile.name}")

    def onContextToggled(self, enabled: bool) -> None:
        """Handle context-sensitive toggle."""
        self.contextSelector.enabled = enabled
        self._updateMappingTable()

    def onContextChanged(self, index: int) -> None:
        """Handle context selector change."""
        self._updateMappingTable()

    def _updateMappingTable(self) -> None:
        """Update the button mapping table based on current profile and preset."""
        import qt

        self.mappingTable.setRowCount(0)

        # Get current profile and preset
        mouseId = self._parameterNode.selectedMouseId if self._parameterNode else ""
        presetId = self._parameterNode.selectedPresetId if self._parameterNode else ""

        if not mouseId or mouseId not in self._mouseProfiles:
            return

        profile = self._mouseProfiles[mouseId]
        preset = self._presetManager.get_preset(presetId) if presetId else None

        # Get current context
        context = None
        if self.contextToggle.checked:
            context = self.contextSelector.currentData

        # Populate table with remappable buttons
        remappable = profile.get_remappable_buttons()
        self.mappingTable.setRowCount(len(remappable))

        for row, button in enumerate(remappable):
            # Button name
            buttonItem = qt.QTableWidgetItem(button.name)
            buttonItem.setData(qt.Qt.UserRole, button.id)
            self.mappingTable.setItem(row, 0, buttonItem)

            # Current action - use combo box for editing
            actionCombo = qt.QComboBox()
            self._populateActionCombo(actionCombo)

            # Get current mapping
            current_action = ""
            if preset:
                mapping = preset.get_mapping(button.id, context)
                if mapping:
                    current_action = mapping.action_id or mapping.action

            # Set current selection
            index = actionCombo.findData(current_action)
            if index >= 0:
                actionCombo.setCurrentIndex(index)

            # Connect signal with button id
            actionCombo.setProperty("buttonId", button.id)
            actionCombo.connect("currentIndexChanged(int)", lambda idx, b=button.id: self._onActionChanged(b, idx))
            self.mappingTable.setCellWidget(row, 1, actionCombo)

            # Clear button
            clearBtn = qt.QPushButton("Clear")
            clearBtn.setMaximumWidth(60)
            clearBtn.connect("clicked()", lambda checked=False, b=button.id: self._onClearMapping(b))
            self.mappingTable.setCellWidget(row, 2, clearBtn)

    def _populateActionCombo(self, combo) -> None:
        """Populate an action combo box with available actions."""
        combo.clear()
        combo.addItem("-- None --", "")

        # Add actions grouped by category
        for category in self._actionRegistry.get_categories():
            actions = self._actionRegistry.get_actions_by_category(category)
            for action in actions:
                combo.addItem(f"{action.description}", action.id)

    def _onActionChanged(self, button_id: str, index: int) -> None:
        """Handle action selection change for a button."""
        presetId = self._parameterNode.selectedPresetId if self._parameterNode else ""
        if not presetId:
            return

        preset = self._presetManager.get_preset(presetId)
        if not preset:
            return

        # Get the combo box that triggered this
        combo = self.sender()
        if not combo:
            return

        action_id = combo.currentData
        context = None
        if self.contextToggle.checked:
            context = self.contextSelector.currentData if self.contextSelector.currentData else None

        if action_id:
            # Set the mapping
            mapping = Mapping(action=action_id)
            preset.set_mapping(button_id, mapping, context)
            logging.info(f"Set mapping: {button_id} -> {action_id} (context: {context})")
        else:
            # Remove the mapping
            preset.remove_mapping(button_id, context)
            logging.info(f"Removed mapping: {button_id} (context: {context})")

        # Save the preset
        self._presetManager.save_preset(preset)
        # Reload into event handler
        self._eventHandler.set_preset(preset)

    def _onClearMapping(self, button_id: str) -> None:
        """Clear the mapping for a button."""
        presetId = self._parameterNode.selectedPresetId if self._parameterNode else ""
        if not presetId:
            return

        preset = self._presetManager.get_preset(presetId)
        if not preset:
            return

        context = None
        if self.contextToggle.checked:
            context = self.contextSelector.currentData if self.contextSelector.currentData else None

        preset.remove_mapping(button_id, context)
        logging.info(f"Cleared mapping: {button_id} (context: {context})")

        # Save the preset
        self._presetManager.save_preset(preset)
        # Reload into event handler
        self._eventHandler.set_preset(preset)
        # Refresh table
        self._updateMappingTable()

    def onDetectClicked(self) -> None:
        """Open the button detection wizard dialog."""
        import qt

        dialog = ButtonDetectionDialog(self.parent)
        if dialog.exec() == qt.QDialog.Accepted:
            # Get the generated profile
            profile = dialog.getProfile()
            if profile:
                # Save the profile
                self._saveDetectedProfile(profile)
                # Refresh the mouse selector
                self._populateMouseSelector()
                # Select the new profile
                index = self.mouseSelector.findData(profile.id)
                if index >= 0:
                    self.mouseSelector.setCurrentIndex(index)
                logging.info(f"Added new mouse profile: {profile.name}")

    def _saveDetectedProfile(self, profile: MouseProfile) -> None:
        """Save a detected mouse profile and create a default preset."""
        from MouseMasterLib.preset_manager import Preset

        user_dir = Path(slicer.app.slicerUserSettingsFilePath).parent / "MouseMaster" / "MouseDefinitions"
        user_dir.mkdir(parents=True, exist_ok=True)
        profile_path = user_dir / f"{profile.id}.json"
        profile.to_json_file(profile_path)
        # Add to loaded profiles
        self._mouseProfiles[profile.id] = profile
        logging.info(f"Saved mouse profile to {profile_path}")

        # Create a default preset for the new mouse
        default_mappings: dict[str, Mapping] = {}
        for button in profile.get_remappable_buttons():
            if button.id == "back":
                # Default: previous module (like Slicer default Ctrl+Left)
                default_mappings[button.id] = Mapping(
                    action="keyboard_shortcut",
                    parameters={"key": "Left", "modifiers": ["ctrl"]}
                )
            elif button.id == "forward":
                # Default: next module (like Slicer default Ctrl+Right)
                default_mappings[button.id] = Mapping(
                    action="keyboard_shortcut",
                    parameters={"key": "Right", "modifiers": ["ctrl"]}
                )
            elif button.id == "middle":
                default_mappings[button.id] = Mapping(action="view_reset_3d")
            elif button.default_action:
                default_mappings[button.id] = Mapping(action=button.default_action)

        # Context mappings for editing modules
        context_mappings: dict[str, dict[str, Mapping]] = {}
        has_back = any(b.id == "back" for b in profile.get_remappable_buttons())
        has_forward = any(b.id == "forward" for b in profile.get_remappable_buttons())
        if has_back or has_forward:
            # SegmentEditor and Markups: undo/redo (editing actions)
            for module in ["SegmentEditor", "Markups"]:
                context_mappings[module] = {}
                if has_back:
                    context_mappings[module]["back"] = Mapping(action="edit_undo")
                if has_forward:
                    context_mappings[module]["forward"] = Mapping(action="edit_redo")
            # VolumeRendering: toggle visibility and reset view (viewing actions)
            context_mappings["VolumeRendering"] = {}
            if has_back:
                context_mappings["VolumeRendering"]["back"] = Mapping(action="volumerendering_toggle")
            if has_forward:
                context_mappings["VolumeRendering"]["forward"] = Mapping(action="view_reset_3d")

        preset = Preset(
            id=f"default_{profile.id}",
            name=f"{profile.name} Default",
            version="1.0",
            mouse_id=profile.id,
            mappings=default_mappings,
            context_mappings=context_mappings,
            author="MouseMaster",
            description=f"Default preset for {profile.name}",
        )
        self._presetManager.save_preset(preset)
        logging.info(f"Created default preset for {profile.name}")

    def _saveApplicationSettings(self) -> None:
        """Save current settings to Slicer application settings for persistence."""
        if not self._parameterNode:
            return
        settings = slicer.app.settings()
        settings.setValue("MouseMaster/selectedMouseId", self._parameterNode.selectedMouseId)
        settings.setValue("MouseMaster/selectedPresetId", self._parameterNode.selectedPresetId)
        settings.setValue("MouseMaster/enabled", self._parameterNode.enabled)
        logging.info("[MouseMaster] Settings saved to application settings")

    def _loadApplicationSettings(self) -> None:
        """Load settings from Slicer application settings."""
        if not self._parameterNode:
            return
        settings = slicer.app.settings()
        mouseId = settings.value("MouseMaster/selectedMouseId", "")
        presetId = settings.value("MouseMaster/selectedPresetId", "")
        enabled = settings.value("MouseMaster/enabled", False)
        # QSettings returns strings for bools, need to convert
        if isinstance(enabled, str):
            enabled = enabled.lower() == "true"
        if mouseId:
            self._parameterNode.selectedMouseId = mouseId
        if presetId:
            self._parameterNode.selectedPresetId = presetId
        if enabled:
            self._parameterNode.enabled = enabled
        logging.info(f"[MouseMaster] Loaded settings: mouse={mouseId!r}, preset={presetId!r}, enabled={enabled}")


#
# ButtonDetectionDialog
#


class ButtonDetectionDialog:
    """Dialog for interactive mouse button detection."""

    def __init__(self, parent=None) -> None:
        import qt

        self._dialog = qt.QDialog(parent)
        self._dialog.setWindowTitle("Detect Mouse Buttons")
        self._dialog.setMinimumWidth(400)
        self._dialog.setMinimumHeight(350)

        self._detector = ButtonDetector()
        self._profile: MouseProfile | None = None

        self._setupUI()

    def _setupUI(self) -> None:
        import qt

        layout = qt.QVBoxLayout(self._dialog)

        # Instructions
        self._instructionLabel = qt.QLabel(
            "This wizard will detect your mouse's button codes.\n\n"
            "Press each button on your mouse when prompted."
        )
        self._instructionLabel.setWordWrap(True)
        layout.addWidget(self._instructionLabel)

        # Prompt label (shows current detection step)
        self._promptLabel = qt.QLabel("Click 'Start Detection' to begin.")
        self._promptLabel.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
        self._promptLabel.setAlignment(qt.Qt.AlignCenter)
        layout.addWidget(self._promptLabel)

        # Detected buttons list
        self._buttonList = qt.QListWidget()
        self._buttonList.setMinimumHeight(100)
        layout.addWidget(self._buttonList)

        # Profile name input
        nameLayout = qt.QHBoxLayout()
        nameLabel = qt.QLabel("Profile Name:")
        self._nameEdit = qt.QLineEdit()
        self._nameEdit.setPlaceholderText("My Custom Mouse")
        nameLayout.addWidget(nameLabel)
        nameLayout.addWidget(self._nameEdit)
        layout.addLayout(nameLayout)

        # Buttons
        buttonLayout = qt.QHBoxLayout()

        self._startButton = qt.QPushButton("Start Detection")
        self._startButton.connect("clicked()", self._onStartClicked)
        buttonLayout.addWidget(self._startButton)

        self._finishButton = qt.QPushButton("Finish Detection")
        self._finishButton.enabled = False
        self._finishButton.connect("clicked()", self._onFinishClicked)
        buttonLayout.addWidget(self._finishButton)

        self._saveButton = qt.QPushButton("Save Profile")
        self._saveButton.enabled = False
        self._saveButton.connect("clicked()", self._onSaveClicked)
        buttonLayout.addWidget(self._saveButton)

        self._cancelButton = qt.QPushButton("Cancel")
        self._cancelButton.connect("clicked()", self._dialog.reject)
        buttonLayout.addWidget(self._cancelButton)

        layout.addLayout(buttonLayout)

        # Install event filter for button detection
        self._eventFilter = _DetectionEventFilter(self._dialog, self._onButtonPress)
        self._dialog.installEventFilter(self._eventFilter)

    def _onStartClicked(self) -> None:
        """Start button detection."""
        self._buttonList.clear()
        self._detector.start_detection(
            on_button=self._onButtonDetected,
            on_complete=self._onDetectionComplete,
            expected_buttons=8,
        )
        self._promptLabel.text = self._detector.get_session().current_prompt
        self._startButton.enabled = False
        self._finishButton.enabled = True
        self._saveButton.enabled = False

    def _onFinishClicked(self) -> None:
        """Finish detection early."""
        session = self._detector.finalize_detection()
        if session:
            self._promptLabel.text = "Detection complete!"
            self._finishButton.enabled = False
            self._saveButton.enabled = len(session.buttons) > 0

    def _onButtonPress(self, qt_button: int) -> bool:
        """Handle a button press during detection."""
        if self._detector.is_detecting():
            return self._detector.on_button_press(qt_button)
        return False

    def _onButtonDetected(self, detected) -> None:
        """Callback when a button is detected."""
        import qt

        item = qt.QListWidgetItem(f"Button {detected.qt_button}: {detected.suggested_name}")
        self._buttonList.addItem(item)
        session = self._detector.get_session()
        if session:
            self._promptLabel.text = session.current_prompt

    def _onDetectionComplete(self, session) -> None:
        """Callback when detection is complete."""
        self._promptLabel.text = "Detection complete!"
        self._finishButton.enabled = False
        self._saveButton.enabled = True

    def _onSaveClicked(self) -> None:
        """Save the detected profile."""
        name = self._nameEdit.text.strip() or "Custom Mouse"
        profile_id = name.lower().replace(" ", "_")

        profile_dict = self._detector.generate_profile(
            profile_id=profile_id,
            profile_name=name,
            vendor="Custom",
        )
        self._profile = MouseProfile.from_dict(profile_dict)
        self._dialog.accept()

    def exec(self) -> int:
        """Show the dialog modally."""
        return self._dialog.exec()

    def getProfile(self) -> MouseProfile | None:
        """Get the generated profile."""
        return self._profile


def _DetectionEventFilter(dialog, on_button_press):
    """Create a Qt event filter for button detection."""
    import qt

    class EventFilter(qt.QObject):
        def __init__(self, parent, callback) -> None:
            super().__init__(parent)
            self._callback = callback
            self._mouse_press = qt.QEvent.MouseButtonPress

        def eventFilter(self, obj, event) -> bool:
            if event.type() == self._mouse_press:
                button = int(event.button())
                # Detect all buttons including standard ones
                if self._callback(button):
                    return True
            return False

    return EventFilter(dialog, on_button_press)


#
# MouseMasterLogic
#


class MouseMasterLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self) -> None:
        """Called when the logic class is instantiated. Can be used for initializing member variables."""
        ScriptedLoadableModuleLogic.__init__(self)

    def getParameterNode(self):
        return MouseMasterParameterNode(super().getParameterNode())

    def getResourcePath(self, filename: str) -> Path:
        """Get path to a resource file.

        :param filename: Resource filename relative to Resources directory
        :return: Full path to resource file
        """
        return Path(__file__).parent / "Resources" / filename


#
# MouseMasterTest
#


class MouseMasterTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """Do whatever is needed to reset the state - typically a scene clear will be enough."""
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here."""
        self.setUp()
        self.test_MouseMaster1()
        self.test_EventHandlerInstall()
        self.test_PresetLoading()
        self.test_ActionRegistry()

    def test_MouseMaster1(self):
        """Test basic module loading and instantiation."""
        self.delayDisplay("Starting basic module test")

        # Test that module can be loaded
        self.assertIsNotNone(slicer.modules.mousemaster)
        self.delayDisplay("Module loaded successfully")

        # Test that logic can be instantiated
        logic = MouseMasterLogic()
        self.assertIsNotNone(logic)
        self.delayDisplay("Logic instantiated successfully")

        # Test that event handler can be created
        handler = MouseMasterEventHandler()
        self.assertIsNotNone(handler)
        self.assertFalse(handler.is_installed)
        self.delayDisplay("Event handler created successfully")

        self.delayDisplay("Basic test passed")

    def test_EventHandlerInstall(self):
        """Test event handler installation and uninstallation."""
        self.delayDisplay("Testing event handler install/uninstall")

        handler = MouseMasterEventHandler()

        # Test installation
        self.assertFalse(handler.is_installed)
        handler.install()
        self.assertTrue(handler.is_installed)
        self.delayDisplay("Event handler installed")

        # Test enable/disable
        self.assertTrue(handler.is_enabled)
        handler.set_enabled(False)
        self.assertFalse(handler.is_enabled)
        handler.set_enabled(True)
        self.assertTrue(handler.is_enabled)
        self.delayDisplay("Enable/disable works")

        # Test uninstallation
        handler.uninstall()
        self.assertFalse(handler.is_installed)
        self.delayDisplay("Event handler uninstalled")

        self.delayDisplay("Event handler test passed")

    def test_PresetLoading(self):
        """Test preset manager functionality."""
        self.delayDisplay("Testing preset loading")

        from pathlib import Path

        # Initialize preset manager
        module_dir = Path(__file__).parent
        project_dir = module_dir.parent
        manager = PresetManager(
            builtin_dir=project_dir / "presets" / "builtin",
        )

        # Load presets
        presets = manager.get_all_presets()
        self.assertGreater(len(presets), 0, "Should have at least one preset")
        self.delayDisplay(f"Loaded {len(presets)} presets")

        # Test getting a specific preset
        preset = manager.get_preset("default_generic_5_button")
        if preset:
            self.assertEqual(preset.id, "default_generic_5_button")
            self.assertIsNotNone(preset.mappings)
            self.delayDisplay("Found default_generic_5_button preset")

        self.delayDisplay("Preset loading test passed")

    def test_ActionRegistry(self):
        """Test action registry functionality."""
        self.delayDisplay("Testing action registry")

        from MouseMasterLib.action_registry import ActionRegistry

        registry = ActionRegistry.get_instance()

        # Test categories exist
        categories = registry.get_categories()
        self.assertGreater(len(categories), 0, "Should have action categories")
        self.delayDisplay(f"Found {len(categories)} action categories")

        # Test actions exist
        actions = registry.get_all_actions()
        self.assertGreater(len(actions), 0, "Should have registered actions")
        self.delayDisplay(f"Found {len(actions)} registered actions")

        # Test specific action exists
        undo_action = registry.get_action("edit_undo")
        self.assertIsNotNone(undo_action, "edit_undo action should exist")
        self.delayDisplay("edit_undo action found")

        self.delayDisplay("Action registry test passed")
