"""Event handling for mouse button interception."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from MouseMasterLib.preset_manager import Preset

logger = logging.getLogger(__name__)


class MouseMasterEventHandler:
    """Application-level event handler for mouse button interception."""

    def __init__(self) -> None:
        self._installed = False
        self._enabled = True
        self._preset: Preset | None = None
        self._qt_handler: object | None = None
        self._platform_adapter: object | None = None
        self._action_registry: object | None = None
        self._on_button_press: Callable[[str, str], None] | None = None
        self._vtk_observers: list[tuple[Any, str]] = []

    def install(self) -> None:
        """Install the event handler on the Qt application and VTK views."""
        if self._installed:
            return

        import slicer

        # Install Qt application event filter
        self._qt_handler = _create_event_filter(self)
        slicer.app.installEventFilter(self._qt_handler)

        # Install VTK observers on slice views and 3D views
        self._install_vtk_observers()

        self._installed = True
        logger.info("Event handler installed")

    def _install_vtk_observers(self) -> None:
        """Install Qt event filters on all view widgets."""
        import slicer

        layoutManager = slicer.app.layoutManager()
        if not layoutManager:
            logger.warning("No layout manager available")
            return

        # Get slice view names and install event filters on their widgets
        for sliceViewName in layoutManager.sliceViewNames():
            sliceWidget = layoutManager.sliceWidget(sliceViewName)
            if sliceWidget:
                # Install on the slice view (the VTK widget)
                view = sliceWidget.sliceView()
                if view:
                    view.installEventFilter(self._qt_handler)
                    self._vtk_observers.append((view, "filter"))
                    logger.debug(f"Installed filter on slice view: {sliceViewName}")

        # Get 3D views and install event filters
        for i in range(layoutManager.threeDViewCount):
            threeDWidget = layoutManager.threeDWidget(i)
            if threeDWidget:
                view = threeDWidget.threeDView()
                if view:
                    view.installEventFilter(self._qt_handler)
                    self._vtk_observers.append((view, "filter"))
                    logger.debug(f"Installed filter on 3D view: {i}")

        logger.info(f"Installed event filters on {len(self._vtk_observers)} view widgets")

    def uninstall(self) -> None:
        """Remove the event handler from the Qt application and views."""
        if not self._installed:
            return

        import slicer

        # Remove event filters from view widgets
        for view, _ in self._vtk_observers:
            try:
                view.removeEventFilter(self._qt_handler)
            except RuntimeError as e:
                # View widget may have been deleted by Qt - this is expected during cleanup
                logger.debug("Could not remove event filter (view likely deleted): %s", e)
        self._vtk_observers.clear()

        # Remove from application
        if self._qt_handler:
            slicer.app.removeEventFilter(self._qt_handler)
            self._qt_handler = None

        self._installed = False
        logger.info("Event handler uninstalled")

    @property
    def is_installed(self) -> bool:
        return self._installed

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def set_preset(self, preset: Preset | None) -> None:
        self._preset = preset
        if preset:
            logger.info(f"Preset loaded: {preset.name}")

    def set_on_button_press(self, callback: Callable[[str, str], None] | None) -> None:
        self._on_button_press = callback

    def handle_button_press(self, qt_event: object) -> bool:
        """Handle a mouse button press event.

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
        logger.info(f"Button: {normalized.button_id}, context: {context}")
        mapping = self._preset.get_mapping(normalized.button_id, context)
        if not mapping:
            logger.info(f"No mapping found for {normalized.button_id}")
            return False

        logger.info(f"Found mapping: {mapping.action}")
        # Execute the action and consume the event
        self._execute_mapping(mapping, normalized, context)
        return True

    def _get_current_context(self) -> str:
        """Get the name of the currently active Slicer module."""
        import slicer.util

        return slicer.util.selectedModule() or "default"

    def _execute_mapping(
        self, mapping: object, normalized: object, context: str
    ) -> None:
        """Execute a button mapping."""
        # Get action registry (lazy load)
        if self._action_registry is None:
            from MouseMasterLib.action_registry import ActionRegistry

            self._action_registry = ActionRegistry.get_instance()

        from MouseMasterLib.action_registry import ActionContext

        action_context = ActionContext(
            module_name=context,
            button_id=normalized.button_id,  # type: ignore
            modifiers=normalized.modifiers,  # type: ignore
        )

        action_type = mapping.action  # type: ignore
        action_id = getattr(mapping, "action_id", None)

        if action_type == "python_command":
            command = mapping.parameters.get("command", "")  # type: ignore[attr-defined]
            if command:
                from MouseMasterLib.action_registry import PythonCommandHandler

                cmd_handler = PythonCommandHandler(command)
                cmd_handler.execute(action_context)
            return

        if action_type == "keyboard_shortcut":
            key = mapping.parameters.get("key", "")  # type: ignore[attr-defined]
            mods = mapping.parameters.get("modifiers", [])  # type: ignore[attr-defined]
            if key:
                from MouseMasterLib.action_registry import KeyboardShortcutHandler

                kb_handler = KeyboardShortcutHandler(key, mods)
                kb_handler.execute(action_context)
            return

        # Default: treat as slicer action
        effective_action_id = action_id or action_type
        self._action_registry.execute(effective_action_id, action_context)  # type: ignore


def _create_event_filter(handler: MouseMasterEventHandler) -> object:
    """Create a Qt event filter that wraps the handler."""
    import qt

    class QtEventFilter(qt.QObject):
        def __init__(self, parent: Any = None) -> None:
            super().__init__(parent)
            self._handler = handler
            self._mouse_press = qt.QEvent.MouseButtonPress
            self._mouse_release = qt.QEvent.MouseButtonRelease
            # Track consumed buttons to also consume their release
            self._consumed_buttons: set[int] = set()

        def eventFilter(self, obj: Any, event: Any) -> bool:
            event_type = event.type()
            if event_type == self._mouse_press:
                button = int(event.button())
                if button > 4:
                    logger.info(f"Press event: button={button}")
                    if self._handler.handle_button_press(event):
                        self._consumed_buttons.add(button)
                        logger.info(f"Consumed press for button {button}")
                        return True
                    logger.info("Press NOT consumed")
            elif event_type == self._mouse_release:
                button = int(event.button())
                if button in self._consumed_buttons:
                    self._consumed_buttons.discard(button)
                    logger.info(f"Consumed release for button {button}")
                    return True
            return False

    return QtEventFilter()
