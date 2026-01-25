"""Event handling for mouse button interception.

This module provides the core event handler that intercepts mouse
button presses and routes them to appropriate actions based on
the current preset configuration.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from MouseMasterLib.preset_manager import Preset

logger = logging.getLogger(__name__)


class MouseMasterEventHandler:
    """Application-level event handler for mouse button interception.

    This handler is installed as a Qt event filter on the application
    to intercept mouse button presses before they reach their targets.
    Based on the current preset, button presses are either:
    - Remapped to actions and consumed
    - Passed through to default Slicer handling

    Usage:
        handler = MouseMasterEventHandler()
        handler.set_preset(preset)
        handler.install()
        # ... later ...
        handler.uninstall()
    """

    def __init__(self) -> None:
        """Initialize the event handler."""
        self._installed = False
        self._enabled = True
        self._preset: Preset | None = None
        self._qt_handler: object | None = None

        # Lazy imports of Slicer modules
        self._platform_adapter: object | None = None
        self._action_registry: object | None = None

        # Callbacks
        self._on_button_press: Callable[[str, str], None] | None = None

    def install(self) -> bool:
        """Install the event handler on the Qt application.

        Returns:
            True if installation succeeded, False otherwise
        """
        if self._installed:
            logger.warning("Event handler already installed")
            return True

        try:
            import slicer

            # Create the Qt event filter
            self._qt_handler = _create_event_filter(self)
            slicer.app.installEventFilter(self._qt_handler)

            self._installed = True
            logger.info("MouseMaster event handler installed")
            return True

        except Exception as e:
            logger.error(f"Failed to install event handler: {e}")
            return False

    def uninstall(self) -> bool:
        """Remove the event handler from the Qt application.

        Returns:
            True if removal succeeded, False otherwise
        """
        if not self._installed:
            return True

        try:
            import slicer

            if self._qt_handler:
                slicer.app.removeEventFilter(self._qt_handler)
                self._qt_handler = None

            self._installed = False
            logger.info("MouseMaster event handler uninstalled")
            return True

        except Exception as e:
            logger.error(f"Failed to uninstall event handler: {e}")
            return False

    @property
    def is_installed(self) -> bool:
        """Check if the handler is installed."""
        return self._installed

    @property
    def is_enabled(self) -> bool:
        """Check if the handler is enabled."""
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the handler.

        When disabled, events pass through without interception.

        Args:
            enabled: Whether to enable the handler
        """
        self._enabled = enabled
        logger.debug(f"Event handler {'enabled' if enabled else 'disabled'}")

    def set_preset(self, preset: Preset | None) -> None:
        """Set the active preset.

        Args:
            preset: The preset to use, or None to disable mapping
        """
        self._preset = preset
        if preset:
            logger.info(f"Active preset: {preset.name}")
        else:
            logger.info("Preset cleared")

    def set_on_button_press(self, callback: Callable[[str, str], None] | None) -> None:
        """Set a callback for button press events.

        The callback receives (button_id, context) for each press.
        Useful for UI updates and button detection.

        Args:
            callback: Callback function or None to clear
        """
        self._on_button_press = callback

    def handle_button_press(self, qt_event: object) -> bool:
        """Handle a mouse button press event.

        Args:
            qt_event: The QMouseEvent

        Returns:
            True if the event was consumed, False to pass through
        """
        if not self._enabled:
            return False

        # Get platform adapter (lazy load)
        if self._platform_adapter is None:
            from MouseMasterLib.platform_adapter import PlatformAdapter

            self._platform_adapter = PlatformAdapter.get_instance()

        # Normalize the event
        normalized = self._platform_adapter.normalize_event(qt_event)  # type: ignore

        # Get current context
        context = self._get_current_context()

        # Notify callback if set
        if self._on_button_press:
            self._on_button_press(normalized.button_id, context)

        # If no preset, pass through
        if not self._preset:
            return False

        # Look up mapping
        mapping = self._preset.get_mapping(normalized.button_id, context)
        if not mapping:
            return False

        # Execute the action
        return self._execute_mapping(mapping, normalized, context)

    def _get_current_context(self) -> str:
        """Get the name of the currently active Slicer module.

        Returns:
            The module name, or "default" if unknown
        """
        try:
            import slicer

            module = slicer.app.moduleManager().currentModule()
            return module if module else "default"
        except Exception:
            return "default"

    def _execute_mapping(
        self, mapping: object, normalized: object, context: str
    ) -> bool:
        """Execute a button mapping.

        Args:
            mapping: The Mapping object
            normalized: The normalized event
            context: The current module context

        Returns:
            True if action executed successfully
        """
        # Get action registry (lazy load)
        if self._action_registry is None:
            from MouseMasterLib.action_registry import ActionRegistry

            self._action_registry = ActionRegistry.get_instance()

        # Build action context
        from MouseMasterLib.action_registry import ActionContext

        action_context = ActionContext(
            module_name=context,
            button_id=normalized.button_id,  # type: ignore
            modifiers=normalized.modifiers,  # type: ignore
        )

        # Handle different action types
        action_type = mapping.action  # type: ignore

        if action_type == "slicer_action" or not hasattr(mapping, "action_id"):
            # Standard registry action
            action_id = getattr(mapping, "action_id", None) or mapping.action  # type: ignore
            return self._action_registry.execute(action_id, action_context)  # type: ignore

        elif action_type == "python_command":
            # Execute Python command
            command = mapping.parameters.get("command", "")  # type: ignore
            if command:
                from MouseMasterLib.action_registry import PythonCommandHandler

                handler = PythonCommandHandler(command)
                return handler.execute(action_context)

        logger.warning(f"Unknown action type: {action_type}")
        return False


def _create_event_filter(handler: MouseMasterEventHandler) -> object:
    """Create a Qt event filter that wraps the handler.

    This function creates the filter class at runtime to avoid
    import-time dependency on Qt.

    Args:
        handler: The MouseMasterEventHandler instance

    Returns:
        A QObject subclass instance that can be used as an event filter
    """
    import qt

    class QtEventFilter(qt.QObject):
        """Qt event filter that intercepts mouse button presses."""

        def __init__(self, parent: object = None) -> None:
            super().__init__(parent)
            self._handler = handler
            self._mouse_press = qt.QEvent.MouseButtonPress

        def eventFilter(self, obj: object, event: object) -> bool:
            """Filter events, intercepting mouse button presses."""
            try:
                if event.type() == self._mouse_press:
                    # Only process non-standard buttons (not left/right for normal clicks)
                    button = int(event.button())
                    if button > 4 and self._handler.handle_button_press(event):
                        return True
                return False
            except Exception as e:
                logger.error(f"Event filter error: {e}")
                return False

    return QtEventFilter()
