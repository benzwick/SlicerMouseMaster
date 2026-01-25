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

#
# MouseMaster
#


class MouseMaster(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

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
See more information in <a href="https://github.com/username/SlicerMouseMaster#readme">module documentation</a>.
""")
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = _("""
This extension was developed by the SlicerMouseMaster contributors.
Based on the Slicer extension template.
""")





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

    def setup(self) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.setup(self)

        # Create programmatic UI for MouseMaster
        self._setupUI()

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = MouseMasterLogic()

        # Initialize MouseMaster components
        self._eventHandler = MouseMasterEventHandler()
        # Presets are in presets/builtin/ at project root (one level up from MouseMaster/)
        module_dir = Path(__file__).parent
        project_dir = module_dir.parent
        self._presetManager = PresetManager(
            builtin_dir=project_dir / "presets" / "builtin",
            user_dir=Path(slicer.app.slicerUserSettingsFilePath).parent / "MouseMaster" / "presets",
        )

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

        # Connect signals
        self.enableButton.connect("toggled(bool)", self.onEnableToggled)
        self.mouseSelector.connect("currentIndexChanged(int)", self.onMouseSelected)
        self.presetSelector.connect("currentIndexChanged(int)", self.onPresetSelected)

        # Add stretch to push widgets to top
        self.layout.addStretch(1)

    def cleanup(self) -> None:
        """Called when the application closes and the module widget is destroyed."""
        self.removeObservers()
        # Uninstall event handler when module is cleaned up
        if self._eventHandler:
            self._eventHandler.uninstall()

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
        # Add built-in mouse profiles
        profiles = ["generic_3_button", "generic_5_button", "logitech_mx_master_3s", "logitech_mx_master_4"]
        for profile_id in profiles:
            self.mouseSelector.addItem(profile_id.replace("_", " ").title(), profile_id)

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
        self._updatePresetSelector()

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

    def test_MouseMaster1(self):
        """Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

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

        self.delayDisplay("Test passed")
