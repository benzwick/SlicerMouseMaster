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
    """Base class for action handlers.

    Action handlers implement specific actions that can be triggered
    by mouse button presses.
    """

    @abstractmethod
    def execute(self, context: ActionContext, **kwargs: Any) -> bool:
        """Execute the action.

        Args:
            context: The action context
            **kwargs: Additional parameters for the action

        Returns:
            True if action executed successfully, False otherwise
        """

    def is_available(self, context: ActionContext) -> bool:
        """Check if the action is currently available.

        Args:
            context: The action context

        Returns:
            True if action can be executed, False otherwise
        """
        return True


class SlicerActionHandler(ActionHandler):
    """Handler for built-in Slicer menu actions."""

    def __init__(self, action_name: str) -> None:
        """Initialize with a Slicer action name.

        Args:
            action_name: The QAction object name in Slicer
        """
        self._action_name = action_name

    def execute(self, context: ActionContext, **kwargs: Any) -> bool:
        """Trigger the Slicer menu action."""
        try:
            from slicer.util import mainWindow

            main = mainWindow()
            if main is None:
                logger.warning("Main window not available")
                return False

            import qt

            action = main.findChild(qt.QAction, self._action_name)
            if action is None:
                logger.warning(f"Action not found: {self._action_name}")
                return False

            action.trigger()
            logger.debug(f"Triggered action: {self._action_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to execute action {self._action_name}: {e}")
            return False


class PythonCommandHandler(ActionHandler):
    """Handler for arbitrary Python commands."""

    def __init__(self, command: str) -> None:
        """Initialize with a Python command.

        Args:
            command: Python code to execute
        """
        self._command = command

    def execute(self, context: ActionContext, **kwargs: Any) -> bool:
        """Execute the Python command."""
        try:
            import slicer

            exec(self._command, {"slicer": slicer, "context": context})
            logger.debug(f"Executed command: {self._command[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            return False


class CallableHandler(ActionHandler):
    """Handler that wraps a callable."""

    def __init__(
        self,
        func: Callable[[ActionContext], bool],
        available_check: Callable[[ActionContext], bool] | None = None,
    ) -> None:
        """Initialize with a callable.

        Args:
            func: Function to call on execute
            available_check: Optional function to check availability
        """
        self._func = func
        self._available_check = available_check

    def execute(self, context: ActionContext, **kwargs: Any) -> bool:
        """Call the wrapped function."""
        try:
            return self._func(context)
        except Exception as e:
            logger.error(f"Handler function failed: {e}")
            return False

    def is_available(self, context: ActionContext) -> bool:
        """Check availability using the provided function."""
        if self._available_check:
            return self._available_check(context)
        return True


@dataclass
class ActionEntry:
    """Entry in the action registry.

    Attributes:
        id: Unique action identifier
        handler: The action handler
        category: Action category for organization
        description: Human-readable description
        icon: Optional icon name
    """

    id: str
    handler: ActionHandler
    category: str
    description: str
    icon: str | None = None


class ActionRegistry:
    """Singleton registry of available actions.

    The ActionRegistry maintains a catalog of all actions that can be
    bound to mouse buttons, including built-in Slicer actions and
    custom extensions.
    """

    _instance: ActionRegistry | None = None

    def __init__(self) -> None:
        """Initialize the registry."""
        self._actions: dict[str, ActionEntry] = {}
        self._categories: dict[str, list[str]] = {}

    @classmethod
    def get_instance(cls) -> ActionRegistry:
        """Get the singleton instance.

        Returns:
            The ActionRegistry singleton
        """
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
        """Register an action.

        Args:
            action_id: Unique identifier
            handler: The action handler
            category: Category for organization
            description: Human-readable description
            icon: Optional icon name
        """
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

        logger.debug(f"Registered action: {action_id} in category {category}")

    def unregister(self, action_id: str) -> bool:
        """Unregister an action.

        Args:
            action_id: The action ID to remove

        Returns:
            True if removed, False if not found
        """
        if action_id not in self._actions:
            return False

        entry = self._actions[action_id]
        del self._actions[action_id]

        if entry.category in self._categories and action_id in self._categories[entry.category]:
            self._categories[entry.category].remove(action_id)

        return True

    def get_action(self, action_id: str) -> ActionEntry | None:
        """Get an action by ID.

        Args:
            action_id: The action ID

        Returns:
            The ActionEntry if found, None otherwise
        """
        return self._actions.get(action_id)

    def execute(self, action_id: str, context: ActionContext, **kwargs: Any) -> bool:
        """Execute an action.

        Args:
            action_id: The action to execute
            context: The action context
            **kwargs: Additional parameters

        Returns:
            True if executed successfully, False otherwise
        """
        entry = self.get_action(action_id)
        if entry is None:
            logger.warning(f"Action not found: {action_id}")
            return False

        if not entry.handler.is_available(context):
            logger.debug(f"Action not available: {action_id}")
            return False

        return entry.handler.execute(context, **kwargs)

    def get_actions_by_category(self, category: str) -> list[ActionEntry]:
        """Get all actions in a category.

        Args:
            category: The category name

        Returns:
            List of actions in the category
        """
        action_ids = self._categories.get(category, [])
        return [self._actions[aid] for aid in action_ids if aid in self._actions]

    def get_categories(self) -> list[str]:
        """Get all category names.

        Returns:
            List of category names
        """
        return list(self._categories.keys())

    def get_all_actions(self) -> list[ActionEntry]:
        """Get all registered actions.

        Returns:
            List of all actions
        """
        return list(self._actions.values())

    def _register_builtin_actions(self) -> None:
        """Register built-in Slicer actions."""
        # Editing actions
        self.register(
            "edit_undo",
            SlicerActionHandler("EditUndoAction"),
            "editing",
            "Undo the last action",
            "undo",
        )
        self.register(
            "edit_redo",
            SlicerActionHandler("EditRedoAction"),
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

        logger.info("Registered built-in actions")

    # Helper methods for built-in actions

    @staticmethod
    def _reset_3d_view(context: ActionContext) -> bool:
        """Reset the 3D view."""
        try:
            import slicer

            layout_manager = slicer.app.layoutManager()
            for i in range(layout_manager.threeDViewCount):
                view = layout_manager.threeDWidget(i).threeDView()
                view.resetFocalPoint()
                view.resetCamera()
            return True
        except Exception as e:
            logger.error(f"Failed to reset 3D view: {e}")
            return False

    @staticmethod
    def _center_crosshair(context: ActionContext) -> bool:
        """Center views on crosshair."""
        try:
            import slicer

            crosshair = slicer.util.getNode("Crosshair")
            if crosshair:
                pos = [0.0, 0.0, 0.0]
                crosshair.GetCursorPositionRAS(pos)
                slicer.util.setSliceViewerLayers(background=None, foreground=None, label=None)
                for node in slicer.util.getNodesByClass("vtkMRMLSliceNode"):
                    node.JumpSliceByCentering(pos[0], pos[1], pos[2])
            return True
        except Exception as e:
            logger.error(f"Failed to center crosshair: {e}")
            return False

    @staticmethod
    def _toggle_crosshair(context: ActionContext) -> bool:
        """Toggle crosshair visibility."""
        try:
            import slicer

            crosshair = slicer.util.getNode("Crosshair")
            if crosshair:
                current = crosshair.GetCrosshairMode()
                if current == 0:  # NoCrosshair
                    crosshair.SetCrosshairMode(1)  # ShowBasic
                else:
                    crosshair.SetCrosshairMode(0)
            return True
        except Exception as e:
            logger.error(f"Failed to toggle crosshair: {e}")
            return False

    @staticmethod
    def _is_segment_editor_active(context: ActionContext) -> bool:
        """Check if Segment Editor is active."""
        return context.module_name == "SegmentEditor"

    @staticmethod
    def _set_segment_editor_effect(effect_name: str) -> Callable[[ActionContext], bool]:
        """Create a handler to set Segment Editor effect."""

        def handler(context: ActionContext) -> bool:
            try:
                import slicer

                editor_widget = slicer.modules.segmenteditor.widgetRepresentation()
                if editor_widget is None:
                    return False
                editor = editor_widget.self().editor
                editor.setActiveEffectByName(effect_name)
                return True
            except Exception as e:
                logger.error(f"Failed to set effect {effect_name}: {e}")
                return False

        return handler

    @staticmethod
    def _next_segment(context: ActionContext) -> bool:
        """Select next segment."""
        try:
            import slicer

            editor_widget = slicer.modules.segmenteditor.widgetRepresentation()
            if editor_widget is None:
                return False
            # Navigate to next segment in the list
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
        except Exception as e:
            logger.error(f"Failed to select next segment: {e}")
            return False

    @staticmethod
    def _previous_segment(context: ActionContext) -> bool:
        """Select previous segment."""
        try:
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
        except Exception as e:
            logger.error(f"Failed to select previous segment: {e}")
            return False
