"""Action registry for Slicer actions.

This module provides a registry of actions that can be triggered by
mouse button presses. Actions include built-in Slicer commands,
module-specific actions, and custom Python commands.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)


@dataclass
class ActionContext:
    """Context information for action execution.

    Attributes:
        module_name: Currently active Slicer module
        button_id: The button that triggered the action
        modifiers: Active modifier keys
        view_name: Name of the view that received the event (if applicable)
    """

    module_name: str | None = None
    button_id: str | None = None
    modifiers: set[str] = field(default_factory=set)
    view_name: str | None = None


class ActionHandler(ABC):
    """Base class for action handlers."""

    @abstractmethod
    def execute(self, context: ActionContext, **kwargs: Any) -> bool:
        """Execute the action."""

    def is_available(self, context: ActionContext) -> bool:
        """Check if the action is currently available."""
        return True


class SlicerActionHandler(ActionHandler):
    """Handler for built-in Slicer menu actions."""

    def __init__(self, action_name: str) -> None:
        self._action_name = action_name

    def execute(self, context: ActionContext, **kwargs: Any) -> bool:
        """Trigger the Slicer menu action."""
        import qt
        from slicer.util import mainWindow

        main = mainWindow()
        if main is None:
            logger.warning("Main window not available")
            return False

        action = main.findChild(qt.QAction, self._action_name)
        if action is None:
            logger.warning(f"Action not found: {self._action_name}")
            return False

        action.trigger()
        return True


class PythonCommandHandler(ActionHandler):
    """Handler for arbitrary Python commands."""

    def __init__(self, command: str) -> None:
        self._command = command

    def execute(self, context: ActionContext, **kwargs: Any) -> bool:
        """Execute the Python command."""
        import slicer

        exec(self._command, {"slicer": slicer, "context": context})
        return True


class KeyboardShortcutHandler(ActionHandler):
    """Handler that simulates keyboard shortcuts."""

    def __init__(self, key: str, modifiers: list[str] | None = None) -> None:
        """Initialize with key and optional modifiers.

        Args:
            key: The key to simulate (e.g., "A", "F5", "Delete")
            modifiers: List of modifiers ("ctrl", "shift", "alt", "meta")
        """
        self._key = key
        self._modifiers = modifiers or []

    def execute(self, context: ActionContext, **kwargs: Any) -> bool:
        """Simulate the keyboard shortcut."""
        import qt
        from slicer.util import mainWindow

        main = mainWindow()
        if main is None:
            return False

        # Build modifier flags
        modifier_map = {
            "ctrl": qt.Qt.ControlModifier,
            "shift": qt.Qt.ShiftModifier,
            "alt": qt.Qt.AltModifier,
            "meta": qt.Qt.MetaModifier,
        }
        modifiers = qt.Qt.NoModifier
        for mod in self._modifiers:
            if mod.lower() in modifier_map:
                modifiers = modifiers | modifier_map[mod.lower()]

        # Map key string to Qt key code
        key_code = getattr(qt.Qt, f"Key_{self._key}", None)
        if key_code is None:
            # Try uppercase
            key_code = getattr(qt.Qt, f"Key_{self._key.upper()}", None)
        if key_code is None:
            logger.warning(f"Unknown key: {self._key}")
            return False

        # Create and post key event
        event = qt.QKeyEvent(qt.QEvent.KeyPress, key_code, modifiers)
        qt.QApplication.postEvent(main.focusWidget() or main, event)
        return True


class CallableHandler(ActionHandler):
    """Handler that wraps a callable."""

    def __init__(
        self,
        func: Callable[[ActionContext], bool],
        available_check: Callable[[ActionContext], bool] | None = None,
    ) -> None:
        self._func = func
        self._available_check = available_check

    def execute(self, context: ActionContext, **kwargs: Any) -> bool:
        """Call the wrapped function."""
        return self._func(context)

    def is_available(self, context: ActionContext) -> bool:
        """Check availability using the provided function."""
        if self._available_check:
            return self._available_check(context)
        return True


@dataclass
class ActionEntry:
    """Entry in the action registry."""

    id: str
    handler: ActionHandler
    category: str
    description: str
    icon: str | None = None


class ActionRegistry:
    """Singleton registry of available actions."""

    _instance: ActionRegistry | None = None

    def __init__(self) -> None:
        self._actions: dict[str, ActionEntry] = {}
        self._categories: dict[str, list[str]] = {}

    @classmethod
    def get_instance(cls) -> ActionRegistry:
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = ActionRegistry()
            cls._instance._register_builtin_actions()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton (for testing)."""
        cls._instance = None

    def register(
        self,
        action_id: str,
        handler: ActionHandler,
        category: str,
        description: str,
        icon: str | None = None,
    ) -> None:
        """Register an action."""
        entry = ActionEntry(
            id=action_id,
            handler=handler,
            category=category,
            description=description,
            icon=icon,
        )
        self._actions[action_id] = entry

        if category not in self._categories:
            self._categories[category] = []
        if action_id not in self._categories[category]:
            self._categories[category].append(action_id)

    def unregister(self, action_id: str) -> bool:
        """Unregister an action."""
        if action_id not in self._actions:
            return False

        entry = self._actions[action_id]
        del self._actions[action_id]

        if entry.category in self._categories and action_id in self._categories[entry.category]:
            self._categories[entry.category].remove(action_id)

        return True

    def get_action(self, action_id: str) -> ActionEntry | None:
        """Get an action by ID."""
        return self._actions.get(action_id)

    def execute(self, action_id: str, context: ActionContext, **kwargs: Any) -> bool:
        """Execute an action."""
        entry = self.get_action(action_id)
        if entry is None:
            logger.warning(f"Action not found: {action_id}")
            return False

        if not entry.handler.is_available(context):
            return False

        return entry.handler.execute(context, **kwargs)

    def get_actions_by_category(self, category: str) -> list[ActionEntry]:
        """Get all actions in a category."""
        action_ids = self._categories.get(category, [])
        return [self._actions[aid] for aid in action_ids if aid in self._actions]

    def get_categories(self) -> list[str]:
        """Get all category names."""
        return list(self._categories.keys())

    def get_all_actions(self) -> list[ActionEntry]:
        """Get all registered actions."""
        return list(self._actions.values())

    def discover_slicer_actions(self) -> int:
        """Discover and register available QActions from Slicer's main window.

        Returns:
            Number of actions discovered and registered
        """
        try:
            import qt
            from slicer.util import mainWindow

            main = mainWindow()
            if main is None:
                logger.warning("Main window not available for action discovery")
                return 0

            count = 0
            # Find all QActions in the main window
            for action in main.findChildren(qt.QAction):
                name = action.objectName()
                text = action.text.replace("&", "")  # Remove accelerator markers

                # Skip empty or system actions
                if not name or not text:
                    continue
                # Skip separators
                if action.isSeparator():
                    continue

                action_id = f"slicer_menu_{name}"

                # Skip if already registered
                if action_id in self._actions:
                    continue

                # Determine category from menu path
                category = "slicer_menus"
                parent = action.parent()
                if parent and hasattr(parent, "title"):
                    menu_title = parent.title().replace("&", "")
                    if menu_title:
                        category = f"menu_{menu_title.lower().replace(' ', '_')}"

                self.register(
                    action_id,
                    SlicerActionHandler(name),
                    category,
                    text,
                    None,
                )
                count += 1

            logger.info(f"Discovered {count} Slicer menu actions")
            return count
        except Exception as e:
            logger.warning(f"Failed to discover Slicer actions: {e}")
            return 0

    def _register_builtin_actions(self) -> None:
        """Register built-in Slicer actions."""
        # Editing actions
        self.register(
            "edit_undo",
            CallableHandler(self._do_undo),
            "editing",
            "Undo the last action",
            "undo",
        )
        self.register(
            "edit_redo",
            CallableHandler(self._do_redo),
            "editing",
            "Redo the last undone action",
            "redo",
        )

        # View actions
        self.register(
            "view_reset_3d",
            CallableHandler(self._reset_3d_view),
            "navigation",
            "Reset 3D view to default orientation",
            "view-reset",
        )
        self.register(
            "view_center_crosshair",
            CallableHandler(self._center_crosshair),
            "navigation",
            "Center view on crosshair position",
            "crosshair",
        )
        self.register(
            "view_toggle_crosshair",
            CallableHandler(self._toggle_crosshair),
            "navigation",
            "Toggle crosshair visibility",
            "crosshair",
        )

        # Segment Editor actions
        self.register(
            "segment_editor_paint",
            CallableHandler(
                self._set_segment_editor_effect("Paint"),
                self._is_segment_editor_active,
            ),
            "segment_editor",
            "Activate Paint effect",
            "paint",
        )
        self.register(
            "segment_editor_erase",
            CallableHandler(
                self._set_segment_editor_effect("Erase"),
                self._is_segment_editor_active,
            ),
            "segment_editor",
            "Activate Erase effect",
            "erase",
        )
        self.register(
            "segment_next",
            CallableHandler(self._next_segment, self._is_segment_editor_active),
            "segment_editor",
            "Select next segment",
            "arrow-down",
        )
        self.register(
            "segment_previous",
            CallableHandler(self._previous_segment, self._is_segment_editor_active),
            "segment_editor",
            "Select previous segment",
            "arrow-up",
        )

        # Markups actions
        self.register(
            "markups_place_fiducial",
            CallableHandler(self._place_fiducial, self._is_markups_active),
            "markups",
            "Start placing fiducial points",
            "fiducial",
        )
        self.register(
            "markups_delete_point",
            CallableHandler(self._delete_markup_point, self._is_markups_active),
            "markups",
            "Delete selected control point",
            "delete",
        )

        # Volume Rendering actions
        self.register(
            "volumerendering_toggle",
            CallableHandler(self._toggle_volume_rendering),
            "volume_rendering",
            "Toggle volume rendering visibility",
            "visibility",
        )

    # Built-in action implementations

    @staticmethod
    def _do_undo(context: ActionContext) -> bool:
        import slicer

        slicer.mrmlScene.Undo()
        return True

    @staticmethod
    def _do_redo(context: ActionContext) -> bool:
        import slicer

        slicer.mrmlScene.Redo()
        return True

    @staticmethod
    def _reset_3d_view(context: ActionContext) -> bool:
        import slicer

        layout_manager = slicer.app.layoutManager()
        for i in range(layout_manager.threeDViewCount):
            view = layout_manager.threeDWidget(i).threeDView()
            view.resetFocalPoint()
            view.resetCamera()
        return True

    @staticmethod
    def _center_crosshair(context: ActionContext) -> bool:
        import slicer

        crosshair = slicer.util.getNode("Crosshair")
        if crosshair:
            pos = [0.0, 0.0, 0.0]
            crosshair.GetCursorPositionRAS(pos)
            for node in slicer.util.getNodesByClass("vtkMRMLSliceNode"):
                node.JumpSliceByCentering(pos[0], pos[1], pos[2])
        return True

    @staticmethod
    def _toggle_crosshair(context: ActionContext) -> bool:
        import slicer

        crosshair = slicer.util.getNode("Crosshair")
        if crosshair:
            current = crosshair.GetCrosshairMode()
            crosshair.SetCrosshairMode(0 if current else 1)
        return True

    @staticmethod
    def _is_segment_editor_active(context: ActionContext) -> bool:
        return context.module_name == "SegmentEditor"

    @staticmethod
    def _set_segment_editor_effect(effect_name: str) -> Callable[[ActionContext], bool]:
        def handler(context: ActionContext) -> bool:
            import slicer

            editor_widget = slicer.modules.segmenteditor.widgetRepresentation()
            if editor_widget is None:
                return False
            editor = editor_widget.self().editor
            editor.setActiveEffectByName(effect_name)
            return True

        return handler

    @staticmethod
    def _next_segment(context: ActionContext) -> bool:
        import slicer

        editor_widget = slicer.modules.segmenteditor.widgetRepresentation()
        if editor_widget is None:
            return False
        editor = editor_widget.self().editor
        segmentation = editor.segmentationNode()
        if segmentation:
            seg = segmentation.GetSegmentation()
            current_id = editor.currentSegmentID()
            ids = [seg.GetNthSegmentID(i) for i in range(seg.GetNumberOfSegments())]
            if current_id in ids:
                idx = ids.index(current_id)
                next_idx = (idx + 1) % len(ids)
                editor.setCurrentSegmentID(ids[next_idx])
        return True

    @staticmethod
    def _previous_segment(context: ActionContext) -> bool:
        import slicer

        editor_widget = slicer.modules.segmenteditor.widgetRepresentation()
        if editor_widget is None:
            return False
        editor = editor_widget.self().editor
        segmentation = editor.segmentationNode()
        if segmentation:
            seg = segmentation.GetSegmentation()
            current_id = editor.currentSegmentID()
            ids = [seg.GetNthSegmentID(i) for i in range(seg.GetNumberOfSegments())]
            if current_id in ids:
                idx = ids.index(current_id)
                prev_idx = (idx - 1) % len(ids)
                editor.setCurrentSegmentID(ids[prev_idx])
        return True

    @staticmethod
    def _is_markups_active(context: ActionContext) -> bool:
        return context.module_name == "Markups"

    @staticmethod
    def _place_fiducial(context: ActionContext) -> bool:
        import slicer

        interaction_node = slicer.app.applicationLogic().GetInteractionNode()
        selection_node = slicer.app.applicationLogic().GetSelectionNode()
        selection_node.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
        interaction_node.SetCurrentInteractionMode(interaction_node.Place)
        return True

    @staticmethod
    def _delete_markup_point(context: ActionContext) -> bool:
        import slicer

        # Get the active markup node
        selection_node = slicer.app.applicationLogic().GetSelectionNode()
        markup_id = selection_node.GetActivePlaceNodeID()
        if not markup_id:
            return False
        markup_node = slicer.mrmlScene.GetNodeByID(markup_id)
        if not markup_node:
            return False
        # Delete the last control point
        n = markup_node.GetNumberOfControlPoints()
        if n > 0:
            markup_node.RemoveNthControlPoint(n - 1)
        return True

    @staticmethod
    def _toggle_volume_rendering(context: ActionContext) -> bool:
        import slicer

        # Find volume rendering display nodes
        vol_rendering_nodes = slicer.util.getNodesByClass("vtkMRMLVolumeRenderingDisplayNode")
        for node in vol_rendering_nodes:
            node.SetVisibility(not node.GetVisibility())
        return True
